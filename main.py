import os
import logging
import multiprocessing
import threading
from multiprocessing import Process, Queue
import psutil
import sys
from multiprocessing import Process


logging.basicConfig(filename='process_manager.log', level=logging.INFO,
                    format='%(asctime)s - %(message)s')
process_log = logging.getLogger('processes')
process_log.setLevel(logging.INFO)

shared_queue = multiprocessing.Queue()
mutex = multiprocessing.Lock()
process_threads = {}
threads = []

choices = {
    "1": "Create Process",
    "2": "List Processes",
    "3": "Create Thread",
    "4": "Terminate Thread",
    "5": "IPC: Send Message",
    "6": "IPC: Recieve Message",
    "7": "Process Synchronization",
    "8": "Exit"
}


def create_process(process_name):
    try:
        child_process = Process(target=process_function, args=(process_name,))
        child_process.start()
        child_process.join()  # Wait for the child process to complete
        logging.info(f"Child process '{process_name}' with PID {child_process.pid} running.")
    except Exception as e:
        logging.error(f" ")


def list_processes():
    process_log.info("List of all the running processes:")

    for proc in psutil.process_iter(attrs=['pid', 'name', 'status']):
        process_info = proc.info
    process_log.info("List of running processes:")

    for process in psutil.process_iter(attrs=['pid', 'ppid', 'name', 'status']):
        process_info = process.info
        pid = process_info['pid']
        ppid = process_info['ppid']
        name = process_info['name']
        status = process_info['status']
        process_log.info(
            f"Process with PID: {pid}, Parent PID: {ppid}, Name: {name}, Status: {status}")
        print(
            f"Process with PID: {pid}, Parent PID: {ppid}, Name: {name}, Status: {status}")
    print('\n')


def process_function(process_name):
    global process_log
    try:
        process_log = logging.getLogger('processes')
        process_log.info(
            f"Child process '{process_name}' with PID {os.getpid()} created")
        process_threads[os.getpid()] = []

        while True:
            print("Options within the process:")
            print("1. Create a thread")
            print("2. List threads")
            print("3. Exit process")
            choice = input("Select an option: ")

            if choice == "1":
                thread_name = input("Enter a name for the thread: ")
                create_thread(thread_name)
            elif choice == "2":
                list_threads()
            elif choice == "3":
                print("Exited process.")
                break
            else:
                print("Invalid option. Try again.")
    except Exception as e:
        process_log.error(f" ")


def create_thread(thread_name, process_pid=None):
    def thread_function():
        logging.info(f"Thread '{thread_name}' created successfully")

    thread = threading.Thread(target=thread_function)
    thread.start()

    # Optionally, you can add the thread to your list of threads.
    threads.append((thread, thread_name))
    process_threads.setdefault(process_pid, []).append((thread, thread_name))

    logging.info(f"Thread '{thread_name}' running")

def list_threads():
    process_pid = os.getpid()
    threads = process_threads.get(process_pid, [])

    if not threads:
        print("No threads in this process.")
    else:
        print("Threads in this process:")
        for thread_id, thread_name in threads:
            print(f"Thread ID: {thread_id}, Name: {thread_name}")


# Create a flag to indicate whether the thread should terminate
terminate_flags = {}

def thread_function(thread_name):
    # Implement your thread's logic here
    while not terminate_flags.get(thread_name, False):
        pass

def terminate_thread(thread_name):
    global threads

    # Set the termination flag for the specified thread
    if thread_name in terminate_flags:
        terminate_flags[thread_name] = True

    for thread, name in threads:
        if name == thread_name:
            thread.join()  # Wait for the thread to complete
            print(f"Thread '{thread_name}' terminated.")
            logging.info(f"Thread '{thread_name}' terminated.")
            threads.remove((thread, name))

def ipc_send_message(message):
    with multiprocessing.Lock():
        # Using a multiprocessing.Pipe for IPC
        parent_conn, child_conn = multiprocessing.Pipe()
        child_conn.send(message)
        print(f"Message sent over IPC: {message}")
        logging.info(f"Message sent over IPC: {message}")


def ipc_receive_message():
    log_file_path = 'process_manager.log'
    received_messages = []

    if not os.path.exists(log_file_path):
        return ["Log file not found"]

    with open(log_file_path, 'r') as log_file:
        lines = log_file.readlines()
        for line in lines:
            if "Message sent over IPC: " in line:
                message = line.split("Message sent over IPC: ")[1].strip()
                received_messages.append(message)

    if received_messages:
        return received_messages
    else:
        return ["No message available"]


def producer(q):
    for item in range(5):
        q.put(item)
        print(f"Producing item {item}")
        logging.info(f"Producing item {item}")


def consumer(q):
    for item in iter(q.get, None):
        print(f"Consuming item {item}")
        logging.info(f"Consuming item {item}")


def process_synchronization():
    print("Demonstrating process synchronization using multiprocessing:")
    logging.info("Demonstrating process synchronization using multiprocessing:")

    q = Queue()
    producer_process = Process(target=producer, args=(q,))
    consumer_process = Process(target=consumer, args=(q,))

    producer_process.start()
    consumer_process.start()

    producer_process.join()

    q.put(None)

    consumer_process.join()

    print("Process synchronization demonstration complete.")
    logging.info("Process synchronization demonstration complete.")

def main():
    while True:

        print("Options:")
        for key, value in choices.items():
            print(f"{key}) {value}")

        choice = input("Enter choice: ")

        if choice == "1":
            process_name = input("Enter process name: ")
            create_process(process_name)

        elif choice == "2":
            list_processes()

        elif choice == "3":
            thread_name = input("Enter thread name: ")
            create_thread(thread_name)

        elif choice == "4":
            thread_name = input("Enter thread name: ")
            terminate_thread(thread_name)

        elif choice == "5":
            message = input("Enter message: ")
            ipc_send_message(message)

        elif choice == "6":
            received_messages = ipc_receive_message()
            if received_messages:
                print('\nReceived messages:')
                for message in received_messages:
                    print(f"- {message}")
            else:
                print("No messages received.")
            print('\n')

        elif choice == "7":
            process_synchronization()

        elif choice == "8":
            print("Exited successfully")
            sys.exit(0)

        else:
            print("Invalid option. Try again.", '\n')


if __name__ == "__main__":
    main()  # Call main function