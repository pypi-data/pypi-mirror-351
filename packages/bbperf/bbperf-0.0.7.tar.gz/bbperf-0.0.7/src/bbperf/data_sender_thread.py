# Copyright (c) 2024 Cloudflare, Inc.
# Licensed under the Apache 2.0 license found in the LICENSE file or at https://www.apache.org/licenses/LICENSE-2.0

import time
import socket
import select

from . import util
from . import const


# falling off the end of this method terminates the process
def run(args, stdout_queue, data_sock, peer_addr, shared_run_mode, shared_udp_sending_rate_pps):
    if args.verbosity:
        stdout_queue.put("data sender: start of process")

    peer_addr_for_udp = peer_addr

    # this (data sender) is running on server (aka reverse flow)
    # for udp, we have to wait for a ping message so we know where to send the data packets
    if args.udp and (peer_addr_for_udp is None):
        while True:
            # blocking
            bytes_read, pkt_from_addr = data_sock.recvfrom(const.BUFSZ)
            if len(bytes_read) == len(const.UDP_PING_MSG):
                if bytes_read.decode() == const.UDP_PING_MSG:
                    peer_addr_for_udp = pkt_from_addr
                    if args.verbosity:
                        stdout_queue.put("data sender: peer address: {}".format(peer_addr_for_udp))
                    break

    # udp autorate
    if args.udp:
        udp_pps = shared_udp_sending_rate_pps.value
        batch_size, delay_between_batches = util.convert_udp_pps_to_batch_info(udp_pps)

    # start sending

    if args.verbosity:
        stdout_queue.put("data sender: sending")

    curr_time_sec = time.time()

    interval_start_time = curr_time_sec
    interval_end_time = interval_start_time + const.SAMPLE_INTERVAL_SEC

    interval_time_sec = 0.0
    interval_send_count = 0
    interval_bytes_sent = 0

    accum_send_count = 0
    accum_bytes_sent = 0

    total_send_counter = 1

    while True:
        curr_time_sec = time.time()

        if (shared_run_mode.value == const.RUN_MODE_CALIBRATING):
            is_calibrated = False
        else:
            is_calibrated = True

        record_type = b'run' if is_calibrated else b'cal'

        # we want to be fast here, since this is data write loop, so use ba.extend

        ba = bytearray()
        ba.extend(b' a ')
        ba.extend(record_type)
        ba.extend(b' ')
        ba.extend(str(curr_time_sec).encode())
        ba.extend(b' ')
        ba.extend(str(interval_time_sec).encode())
        ba.extend(b' ')
        ba.extend(str(interval_send_count).encode())
        ba.extend(b' ')
        ba.extend(str(interval_bytes_sent).encode())
        ba.extend(b' ')
        ba.extend(str(total_send_counter).encode())
        ba.extend(b' b ')

        if args.udp:
            ba.extend(const.PAYLOAD_1K)
        elif is_calibrated:
            ba.extend(const.PAYLOAD_4K)
        else:
            ba.extend(const.PAYLOAD_1K)

        try:
            # blocking
            # we want to block here, as blocked time should "count"

            # we use select to take advantage of tcp_notsent_lowat
            _, _, _ = select.select( [], [data_sock], [])

            if args.udp:
                num_bytes_sent = data_sock.sendto(ba, peer_addr_for_udp)
            else:
                # tcp
                num_bytes_sent = data_sock.send(ba)

            if num_bytes_sent <= 0:
                msg = "ERROR: send failed"
                stdout_queue.put(msg)
                raise Exception(msg)

        except ConnectionResetError:
            stdout_queue.put("Connection reset by peer")
            # exit process
            break

        except BrokenPipeError:
            # this can happen at the end of a tcp reverse test
            stdout_queue.put("broken pipe error")
            # exit process
            break

        except BlockingIOError:
            # same as EAGAIN EWOULDBLOCK
            # we did not send, loop back up and try again
            continue

        except socket.timeout:
            # we did not send
            # the timeout value here is 20 seconds, so that is end of days -- kill everything
            error_msg = "FATAL: data_sender_thread: socket timeout"
            stdout_queue.put(error_msg)
            raise Exception(error_msg)

        total_send_counter += 1
        accum_send_count += 1
        accum_bytes_sent += num_bytes_sent

        if curr_time_sec > interval_end_time:
            interval_time_sec = curr_time_sec - interval_start_time
            interval_send_count = accum_send_count
            interval_bytes_sent = accum_bytes_sent

            if args.verbosity > 2:
                print("data_sender: a {} {} {} {} {} {} b".format(
                    record_type, curr_time_sec, interval_time_sec, interval_send_count, interval_bytes_sent, total_send_counter)
                )

            interval_start_time = curr_time_sec
            interval_end_time = interval_start_time + const.SAMPLE_INTERVAL_SEC
            accum_send_count = 0
            accum_bytes_sent = 0

            # update udp autorate
            if args.udp:
                udp_pps = shared_udp_sending_rate_pps.value
                batch_size, delay_between_batches = util.convert_udp_pps_to_batch_info(udp_pps)

        # send very slowly at first to establish unloaded latency
        if not is_calibrated:
            time.sleep(0.2)
            # initialize batch variables here in case next loop is batch processing
            current_batch_start_time = time.time()
            current_batch_counter = 0
            continue

        # normal end of test
        if shared_run_mode.value == const.RUN_MODE_STOP:
            break

        # pause between udp batches if necessary
        if args.udp:
            current_batch_counter += 1
            if current_batch_counter >= batch_size:
                this_delay = delay_between_batches - (curr_time_sec - current_batch_start_time)
                if this_delay > 0:
                    time.sleep(delay_between_batches)
                current_batch_start_time += delay_between_batches
                current_batch_counter = 0


    # send STOP message
    if args.udp:
        if args.verbosity:
            stdout_queue.put("data sender: sending udp stop message")
        payload_bytes = const.UDP_STOP_MSG.encode()
        # 3 times just in case the first one does not make it to the destination
        data_sock.sendto(payload_bytes, peer_addr_for_udp)
        time.sleep(0.1)
        data_sock.sendto(payload_bytes, peer_addr_for_udp)
        time.sleep(0.1)
        data_sock.sendto(payload_bytes, peer_addr_for_udp)

    util.done_with_socket(data_sock)

    if args.verbosity:
        stdout_queue.put("data sender: end of process")
