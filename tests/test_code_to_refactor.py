# This is a sample Python file that could benefit from refactoring


def calculate_sum_and_average(numbers):
    total = 0
    count = 0
    for i in range(len(numbers)):
        total = total + numbers[i]
        count = count + 1

    avg = total / count
    return total, avg


def process_data(data_list):
    result = []
    for item in data_list:
        if item > 0:
            result.append(item * 2)
        else:
            result.append(0)
    return result


def find_max_min(values):
    max_val = values[0]
    min_val = values[0]
    for val in values:
        if val > max_val:
            max_val = val
        if val < min_val:
            min_val = val
    return max_val, min_val


# Main execution
if __name__ == "__main__":
    numbers = [1, 2, 3, 4, 5]
    total, average = calculate_sum_and_average(numbers)
    print(f"Total: {total}, Average: {average}")

    processed = process_data(numbers)
    print(f"Processed: {processed}")

    max_val, min_val = find_max_min(numbers)
    print(f"Max: {max_val}, Min: {min_val}")
