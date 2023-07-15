import requests
import random
import time
import socket
import matplotlib.pyplot as plt
import matplotlib.backends.backend_pdf as pdf_backend
import numpy as np
from datetime import datetime
import ast

""" Generate line graph from data"""


def measure_http_response_time(url, count):
    """ Collect HTTP, TCP and DNS response times for a given URL """
    status = ""
    result = ""
    http_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,\
        image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)\
         Chrome/112.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"'
    }
    try:
        dns_response_time = get_dns_response_time(url)
        if dns_response_time is None:
            raise ValueError("DNS response time measurement failed")

        tcp_connection_time = get_tcp_connection_time(url)
        if tcp_connection_time is None:
            raise ValueError("TCP connection time measurement failed")

        req_start_time = time.time()
        response = requests.get(url, headers=http_headers)
        req_end_time = time.time()
        total_response_time_ms = (req_end_time - req_start_time) * 1000
        http_response_time_ms = total_response_time_ms - (dns_response_time + tcp_connection_time)
        result = (count, http_response_time_ms, dns_response_time, tcp_connection_time)
    except requests.exceptions.RequestException as request_error:
        print(f"Request for {url} error: {request_error}")
    except Exception as error:
        print(f"An Error occurred for {url}: {error}")
    else:
        if response.status_code == 200 and ('application/javascript' in response.headers['Content-Type'] or 'text/html' in response.headers['Content-Type']) and len(response.content) > 0:
            rsp_code = response.status_code
            status = f"REQ_URL: {url}, RSP_CODE: {rsp_code}, REQ_START: {req_start_time}, REQ_END: {req_end_time},HTTP_RESP_TIME: {http_response_time_ms}, DNS_RESP_TIME: {dns_response_time}, TCP_CONN_TIME: {tcp_connection_time}"
        else:
            status = f"REQ_URL: {url}, RSP_CODE: {rsp_code}, REQ_START: {req_start_time}, REQ_END: {req_end_time},HTTP_RESP_TIME: {http_response_time_ms}, DNS_RESP_TIME: {dns_response_time}, TCP_CONN_TIME: {tcp_connection_time}"

    return status, result


def get_dns_response_time(url):
    """ Measure DNS response time - use cache """
    domain = url.split('/')[2]
    try:
        dns_start_time = time.time()
        socket.gethostbyname(domain)
    except socket.gaierror as dns_error:
        print(f"DNS Resolution Error for {url}: {dns_error}")
        return None
    except Exception as dns_error:
        print(f"An Error occurred for {url}: {dns_error}")
        return None
    else:
        dns_end_time = time.time()
        dns_response_time_ms = (dns_end_time - dns_start_time) * 1000
    return dns_response_time_ms


def get_tcp_connection_time(url):
    """ Measure TCP connection time """
    domain = url.split('/')[2]
    try:
        tcp_start_time = time.time()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((domain, 443))
    except ConnectionResetError as reset_rcv:
        print(f"TCP Connection Reset Error for {url}: {reset_rcv}")
        return None
    except Exception as tcp_error:
        print(f"TCP Connection Error for {url}: {tcp_error}")
        return None
    else:
        try:
            tcp_end_time = time.time()
            tcp_connection_time_ms = (tcp_end_time - tcp_start_time) * 1000
            s.close()
        except Exception as tcp_close_error:
            print(f"TCP Connection Close Error for {url}: {tcp_close_error}")
            return None

    return tcp_connection_time_ms


def measure_execution_time(func):
    """ Measure execution time of a function - Not implemented yet """
    start_time = time.perf_counter()
    func()
    end_time = time.perf_counter()
    execution_time = end_time - start_time
    return execution_time


def http_test_begin(test_url, test_duration, min_interval, max_interval):
    """ Here is the main calling function """

    start_time = time.time()
    end_time = start_time + test_duration

    """ Create a human readable results file """
    human_readable_results_file = f"human_readable_results_file{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"

    """ Create an empty list to store results 'data'  - set iteration count to 0 (always) """
    data = []
    iteration = 0

    """ While UTC time is less than end time, keep running the tests 
        Increment iteration by 1 for each run 
        status and result values come back from measure_http_response_time function
        status is a human readable string and result is a tuple of values
        Result gets appended to the results list. 
    """
    try:
        while time.time() < end_time:
            iteration += 1
            status, measurements = measure_http_response_time(test_url, iteration)
            data.append(measurements)
            print(f"Test Iteration: {iteration}")
            print(status)
            with open(human_readable_results_file, "a") as file:
                file.write(f"{status}\n")
            time.sleep(random.randint(min_interval, max_interval))

    except Exception as error:
        print(f"Error occurred: {error}")
        return None, None

    else:
        try:
            print("Generating HTTP Latency Graph")
            http_g_name = generate_http_response_time_graph(data)
            if http_g_name is None:
                """ check data that was passed to function"""
                iteration, http_response_time_ms, _, _ = zip(*data)
                raise ValueError(f"Error generating graph: {http_response_time_ms[0:5]}")
            else:
                print("Done..")
                print("Generating TCP Latency Graph")
            tcp_g_name = generate_tcp_response_time_graph(data)
            if tcp_g_name is None:
                """ check data that was passed to function"""
                iteration, _, tcp_connection_time_ms, _ = zip(*data)
                raise ValueError(f"Error generating graph: {tcp_connection_time_ms[0:5]}")
            else:
                print("Done..")
                print("Generating DNS Latency Graph")
            dns_g_name = generate_dns_response_time_graph(data)
            if dns_g_name is None:
                """ check data that was passed to function"""
                iteration, _, _, dns_response_time_ms = zip(*data)
                raise ValueError(f"Error generating graph: {dns_response_time_ms[0:5]}")
            else:
                print("Done..")
                print("Finishing up...")
        except Exception as error:
            print(f"Error generating graph: {error}")
            return data, None, None, None

    return data, http_g_name, tcp_g_name, dns_g_name


def generate_http_response_time_graph(http_results):
    """ Generate HTTP Response Time Graph """
    http_graph_name = f"http_response_time_graph_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"

    if not http_results:
        print("No results to generate report")
        return None

    iteration, http_times, _, _ = zip(*http_results)
    total_requests = len(iteration)
    num_requests_per_dot = 1 if total_requests <= 50 else int(total_requests / 50)

    if len(iteration) > 50:
        mean_interval = int(len(iteration) / 50)
        iteration_mean = []
        http_times_mean = []
        for i in range(0, len(iteration), mean_interval):
            subset_iteration = iteration[i:i+mean_interval]
            subset_http_times = http_times[i:i+mean_interval]
            iteration_mean.append(np.mean(subset_iteration))
            http_times_mean.append(np.mean(subset_http_times))
            x = iteration_mean
            y = http_times_mean
    else:
        x = iteration
        y = http_times

    plt.figure(figsize=(13, 8))

    plt.plot(x, y, marker='o', linestyle='-', color='blue')

    plt.xlabel("Iteration")
    plt.ylabel("Time (ms)")
    plt.title("HTTP Response Latency")

    min_latency = np.min(http_times)
    max_latency = np.max(http_times)
    mean_latency = np.mean(http_times)

    text_str = f"Minimum Latency: {min_latency} ms\n"
    text_str += f"Maximum Latency: {max_latency} ms\n"
    text_str += f"Mean Latency: {mean_latency} ms\n"
    text_str += f"Total Requests: {total_requests}\n"
    text_str += f"Number of Requests per Dot: {num_requests_per_dot}"

    plt.text(0.02, 0.98, text_str, transform=plt.gca().transAxes, verticalalignment='top')

    plt.gca().yaxis.set_minor_locator(plt.MultipleLocator(10))
    plt.savefig(http_graph_name)

    return http_graph_name


def generate_tcp_response_time_graph(tcp_results):

    tcp_graph_name = f"tcp_response_time_graph_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"

    if tcp_results is None:
        print("No results to generate report")
        return None

    iteration, _, _, tcp_times = zip(*tcp_results)
    total_requests = len(iteration)
    num_requests_per_dot = 1 if total_requests <= 50 else int(total_requests / 50)

    if len(iteration) > 50:
        mean_interval = int(len(iteration) / 50)
        iteration_mean = []
        tcp_times_mean = []
        for i in range(0, len(iteration), mean_interval):
            subset_iteration = iteration[i:i+mean_interval]
            subset_tcp_times = tcp_times[i:i+mean_interval]
            iteration_mean.append(np.mean(subset_iteration))
            tcp_times_mean.append(np.mean(subset_tcp_times))
        x = iteration_mean
        y = tcp_times_mean
    else:
        x = iteration
        y = tcp_times

    plt.figure(figsize=(13, 8))

    plt.plot(x, y, marker='o', linestyle='-', color='blue')

    plt.xlabel("Iteration")
    plt.ylabel("Time (ms)")
    plt.title("TCP Connection Time")

    min_latency = np.min(tcp_times)
    max_latency = np.max(tcp_times)
    mean_latency = np.mean(tcp_times)

    text_str = f"Minimum Latency: {min_latency} ms\n"
    text_str += f"Maximum Latency: {max_latency} ms\n"
    text_str += f"Mean Latency: {mean_latency} ms\n"
    text_str += f"Total Requests: {total_requests}\n"
    text_str += f"Number of Requests per Dot: {num_requests_per_dot}"

    plt.text(0.02, 0.98, text_str, transform=plt.gca().transAxes, verticalalignment='top')

    plt.gca().yaxis.set_minor_locator(plt.MultipleLocator(1))
    plt.savefig(tcp_graph_name)

    return tcp_graph_name


def generate_dns_response_time_graph(dns_results):

    dns_graph_name = f"dns_response_time_graph_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"

    if not dns_results:
        print("No results to generate report")
        return None

    iteration, _, dns_times, _ = zip(*dns_results)
    total_requests = len(iteration)
    num_requests_per_dot = 1 if total_requests <= 50 else int(total_requests / 50)

    if len(iteration) > 50:
        mean_interval = int(len(iteration) / 50)
        iteration_mean = []
        dns_times_mean = []
        for i in range(0, len(iteration), mean_interval):
            subset_iteration = iteration[i:i+mean_interval]
            subset_dns_times = dns_times[i:i+mean_interval]
            iteration_mean.append(np.mean(subset_iteration))
            dns_times_mean.append(np.mean(subset_dns_times))
        x = iteration_mean
        y = dns_times_mean
    else:
        x = iteration
        y = dns_times

    plt.figure(figsize=(13, 8))

    plt.plot(x, y, marker='o', linestyle='-', color='blue')

    plt.xlabel("Iteration")
    plt.ylabel("Time (ms)")
    plt.title("DNS Response Time")

    min_latency = np.min(dns_times)
    max_latency = np.max(dns_times)
    mean_latency = np.mean(dns_times)

    text_str = f"Minimum Latency: {min_latency} ms\n"
    text_str += f"Maximum Latency: {max_latency} ms\n"
    text_str += f"Mean Latency: {mean_latency} ms\n"
    text_str += f"Total Requests: {total_requests}\n"
    text_str += f"Number of Requests per point: {num_requests_per_dot}"

    plt.text(0.02, 0.98, text_str, transform=plt.gca().transAxes, verticalalignment='top')

    plt.gca().yaxis.set_minor_locator(plt.MultipleLocator(5))
    plt.savefig(dns_graph_name)

    return dns_graph_name


def generate_pdf(output_filename, raw, http_png, tcp_png, dns_png):

    pdf = pdf_backend.PdfPages(output_filename)

    # Add HTTP graph
    http_graph = plt.imread(http_png)
    plt.figure(figsize=(13, 8))
    plt.imshow(http_graph)
    plt.axis('off')
    pdf.savefig()
    plt.close()

    # Add TCP graph
    tcp_graph = plt.imread(tcp_png)
    plt.figure(figsize=(13, 8))
    plt.imshow(tcp_graph)
    plt.axis('off')
    pdf.savefig()
    plt.close()

    # Add DNS graph
    dns_graph = plt.imread(dns_png)
    plt.figure(figsize=(13, 8))
    plt.imshow(dns_graph)
    plt.axis('off')
    pdf.savefig()
    plt.close()

    #Add raw results table
    with open(raw, "r") as f:
        table_data = f.read()

    table_data = table_data.split("\n")

    # Remove empty entries

    clean_table = [row for row in table_data if row]

    # Convert from list of strings to a list of tuples.
    # Each tuple represents a row in the table

    tuple_list = [eval(entry) for entry in clean_table]

    # Build the columns for the table by extracting the data from each tuple into its own list.

    iterations = [row[0] for row in tuple_list]
    http_latency = [row[1] for row in tuple_list]
    dns_latency = [row[2] for row in tuple_list]
    tcp_latency = [row[3] for row in tuple_list]

    measurements = [iterations, http_latency, dns_latency, tcp_latency]

    # To get this working, you have to create a transposed list. So this means, using zip() to join the lists together.

    transposed_measurements = list(zip(*measurements))
    col_labels = ["Iteration", "HTTP Latency", "DNS Latency", "TCP Latency"]

    # Error logic to be implemented in the next version.

    try:
        plt.figure(figsize=(8, 40))
        plt.axis('off')
        plt.table(cellText=transposed_measurements, colLabels=col_labels, loc='center')
        pdf.savefig()
        plt.close()
    except Exception as error:
        print(f"Error generating table: {error}")
        print(f"Table data: {measurements}")
        print(f"Column labels: {col_labels}")
    else:
        pdf.close()

    return True


if __name__ == "__main__":
    tst_url = "https://cttools.co.uk/shape_sed.html"
    """Suggested Conservative Samples: 1800 (30 minutes, 10sec, 31sec or 900 (15 minutes), 3s, 10s"""
    """Suggested Aggressive Samples: 1800 (30 minutes, 3sec, 10sec or 900 (15 minutes), 3s, 10s"""
    test_length = 1800
    min_int = 10
    max_int = 31
    results, http_visual_png, tcp_visual_png, dns_visual_png = http_test_begin(tst_url, test_length, min_int, max_int)
    raw_results = f"raw_results_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
    pdf_results_filename = f"graphed_results_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"

    with open(raw_results, "a") as f:
        for result in results:
            f.write(str(result) + "\n")

    result = generate_pdf(pdf_results_filename, raw_results, http_visual_png, tcp_visual_png, dns_visual_png)

    if result:
        print("PDF successfully generated")
    else:
        print("Error occurred during PDF generation")

"""    if graph:
        graph.show()
    else:
        print("No graph to show")"""


"""
execution_time = measure_execution_time(lambda: get_dns_response_time("https://www.google.com/"))
print("Execution time:", execution_time, "seconds")"""