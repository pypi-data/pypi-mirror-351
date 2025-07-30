# Copyright (c) 2024 Cloudflare, Inc.
# Licensed under the Apache 2.0 license found in the LICENSE file or at https://www.apache.org/licenses/LICENSE-2.0

import time

from . import util

from .exceptions import PeerDisconnectedException
from .udp_rate_manager_class import UdpRateManagerClass
from .run_mode_manager_class import RunModeManagerClass

# direction up, runs on client
# args are client args (not server args)
# falling off the end of this method terminates the process
def run_recv_term_queue(args, stdout_queue, control_conn, results_queue, shared_run_mode, shared_udp_sending_rate_pps):
    if args.verbosity:
        stdout_queue.put("starting control receiver process: run_recv_term_queue")

    run_mode_manager = RunModeManagerClass(args, shared_run_mode)
    udp_rate_manager = UdpRateManagerClass(args, shared_udp_sending_rate_pps)

    while True:

        try:
            # blocking
            bytes_read = control_conn.recv_a_c_block()

        except ConnectionResetError:
            if args.verbosity:
                stdout_queue.put("connection reset error")
            # exit process
            break

        except PeerDisconnectedException:
            if args.verbosity:
                stdout_queue.put("peer disconnected (control socket)")
            # exit process
            break

        curr_time_str = str(time.time())

        received_str = bytes_read.decode()

        # the zeroes will be updated below
        tmp_str = received_str + curr_time_str + " 0 0 0 d "

        r_record = util.parse_r_record(args, tmp_str)

        # updates   shared_run_mode
        #           r_record["interval_dropped"]
        #           r_record["interval_dropped_percent"]
        #           r_record["is_sample_valid"]
        run_mode_manager.update(r_record)

        if args.udp:
            udp_rate_manager.update(r_record)

        new_str = (received_str + curr_time_str + " " +
                    str(r_record["interval_dropped"]) + " " +
                    str(r_record["interval_dropped_percent"]) + " " +
                    str(r_record["is_sample_valid"]) + " d ")

        results_queue.put(new_str)

        if args.verbosity > 1:
            stdout_queue.put("control receiver process: created: {}".format(new_str))

    control_conn.close()

    if args.verbosity:
        stdout_queue.put("exiting control receiver process: run_recv_term_queue")


# direction down, runs on server
# args are client args (not server args)
# falling off the end of this method terminates the process
def run_recv_term_send(args, stdout_queue, control_conn, shared_run_mode, shared_udp_sending_rate_pps):
    if args.verbosity:
        stdout_queue.put("starting control receiver process: run_recv_term_send")

    run_mode_manager = RunModeManagerClass(args, shared_run_mode)
    udp_rate_manager = UdpRateManagerClass(args, shared_udp_sending_rate_pps)

    while True:

        try:
            # blocking
            bytes_read = control_conn.recv_a_c_block()

        except ConnectionResetError:
            if args.verbosity:
                stdout_queue.put("connection reset error")
            # exit process
            break

        except PeerDisconnectedException:
            if args.verbosity:
                stdout_queue.put("peer disconnected (control socket)")
            # exit process
            break

        curr_time_str = str(time.time())

        received_str = bytes_read.decode()

        # the zeroes will be updated below
        tmp_str = received_str + curr_time_str + " 0 0 0 d "

        r_record = util.parse_r_record(args, tmp_str)

        # updates   shared_run_mode
        #           r_record["interval_dropped"]
        #           r_record["interval_dropped_percent"]
        #           r_record["is_sample_valid"]
        run_mode_manager.update(r_record)

        if args.udp:
            udp_rate_manager.update(r_record)

        new_str = (received_str + curr_time_str + " " +
                    str(r_record["interval_dropped"]) + " " +
                    str(r_record["interval_dropped_percent"]) + " " +
                    str(r_record["is_sample_valid"]) + " d ")

        control_conn.send(new_str.encode())

        if args.verbosity > 1:
            stdout_queue.put("control receiver process: created: {}".format(new_str))


    control_conn.close()

    if args.verbosity:
        stdout_queue.put("exiting control receiver process: run_recv_term_send")


# direction down, runs on client (passthru)
# args are client args (not server args) -- this always runs on client
# falling off the end of this method terminates the process
def run_recv_queue(args, stdout_queue, control_conn, results_queue):
    if args.verbosity:
        stdout_queue.put("starting control receiver process: run_recv_queue")

    while True:
        try:
            # blocking
            bytes_read = control_conn.recv_a_d_block()

        except ConnectionResetError:
            if args.verbosity:
                stdout_queue.put("connection reset error")
            # exit process
            break

        except PeerDisconnectedException:
            if args.verbosity:
                stdout_queue.put("peer disconnected (control socket)")
            # exit process
            break

        received_str = bytes_read.decode()

        # passthru as is
        results_queue.put(received_str)

    control_conn.close()

    if args.verbosity:
        stdout_queue.put("exiting control receiver process: run_recv_queue")
