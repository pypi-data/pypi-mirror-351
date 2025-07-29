def quick_sort(arr, reverse=False):
    if len(arr) <= 1:
        return arr

    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]

    # 递归调用时不传递 reverse 参数，仅在最终结果中应用 reverse
    result = quick_sort(left) + middle + quick_sort(right)
    return result[::-1] if reverse else result

def shell_sort(arr, reverse=False):
    n = len(arr)
    gap = n // 2  # 初始增量
    
    while gap > 0:
        for i in range(gap, n):
            temp = arr[i]
            j = i
            # 对当前增量的子序列进行插入排序
            while j >= gap and arr[j - gap] > temp:
                arr[j] = arr[j - gap]
                j -= gap
            arr[j] = temp
        gap //= 2  # 减小增量
    return arr[::-1] if reverse else arr

def heap_sort(arr, reverse=False):
    import heapq
    arr = list(arr)  # 复制输入列表，避免修改原始数据
    if not arr:
        return arr
    heapq.heapify(arr)
    result = [heapq.heappop(arr) for _ in range(len(arr))]
    return result[::-1] if reverse else result

def bucket_sort(arr, reverse=False):
    if not arr:
        return arr

    max_val = max(arr)
    min_val = min(arr)
    range_val = max_val - min_val

    if range_val == 0:
        return arr  # 如果所有元素相同，直接返回

    # 动态调整桶数量
    bucket_count = max(10, int(len(arr) ** 0.5))  # 桶数量为 sqrt(n) 或至少 10
    buckets = [[] for _ in range(bucket_count)]

    for num in arr:
        index = int((num - min_val) * (bucket_count - 1) / range_val)
        buckets[index].append(num)

    sorted_arr = []
    for bucket in buckets:
        sorted_arr.extend(sorted(bucket))

    return sorted_arr[::-1] if reverse else sorted_arr

def insertion_sort(arr, reverse=False):
    if not arr:
        return arr
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and key < arr[j]:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr[::-1] if reverse else arr

def bubble_sort(arr, reverse=False):
    if not arr:
        return arr
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr[::-1] if reverse else arr

def merge_sort(arr, reverse=False):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    
    merged = []
    left_idx, right_idx = 0, 0
    while left_idx < len(left) and right_idx < len(right):
        if left[left_idx] < right[right_idx]:
            merged.append(left[left_idx])
            left_idx += 1
        else:
            merged.append(right[right_idx])
            right_idx += 1
    merged.extend(left[left_idx:])
    merged.extend(right[right_idx:])
    return merged[::-1] if reverse else merged

def selection_sort(arr, reverse=False):
    if not arr:
        return arr
    for i in range(len(arr)):
        min_idx = i
        for j in range(i+1, len(arr)):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr[::-1] if reverse else arr

def counting_sort(arr, reverse=False):
    if not arr:
        return arr
    max_val = max(arr)
    min_val = min(arr)
    offset = -min_val  # 添加偏移量以支持负数
    count = [0] * (max_val - min_val + 1)
    for num in arr:
        count[num + offset] += 1
    sorted_arr = []
    for i in range(len(count)):
        sorted_arr.extend([i - offset] * count[i])  # 还原原始值
    return sorted_arr[::-1] if reverse else sorted_arr

def radix_sort(arr, reverse=False):
    if not arr:
        return arr
    
    # 分离负数和非负数
    negatives = [-x for x in arr if x < 0]
    non_negatives = [x for x in arr if x >= 0]
    
    def radix_sort_non_negative(nums):
        max_val = max(nums) if nums else 0
        exp = 1
        while max_val // exp > 0:
            count = [0] * 10
            output = [0] * len(nums)
            for num in nums:
                index = (num // exp) % 10
                count[index] += 1
            for i in range(1, 10):
                count[i] += count[i-1]
            i = len(nums) - 1
            while i >= 0:
                index = (nums[i] // exp) % 10
                output[count[index]-1] = nums[i]
                count[index] -= 1
                i -= 1
            nums = output.copy()
            exp *= 10
        return nums
    
    # 对负数和非负数分别排序
    negatives_sorted = [-x for x in radix_sort_non_negative(negatives)[::-1]]
    non_negatives_sorted = radix_sort_non_negative(non_negatives)
    
    result = negatives_sorted + non_negatives_sorted
    return result[::-1] if reverse else result

def value_range_mapping_sort(nums, reverse=False):
    if not nums:
        return []

    min_val, max_val = min(nums), max(nums)
    range_size = max_val - min_val + 1\
    
    # 如果值域过大，回退到 Timsort
    if max_val - min_val > len(nums) * 10:
        return sorted(nums)  # 回退到 Timsort

    # 计数
    count = [0] * range_size
    for num in nums:
        count[num - min_val] += 1

    # 起始位置表
    start_positions = [0] * range_size
    for i in range(1, range_size):
        start_positions[i] = start_positions[i - 1] + count[i - 1]

    # 构造结果，保持稳定性
    result = [0] * len(nums)
    for num in reversed(nums):  # 逆序遍历以保持稳定性
        idx = num - min_val
        pos = start_positions[idx]  # 注意：这里不需要减一，start_positions 是“第一个可用位置”
        result[pos] = num
        start_positions[idx] += 1  # 更新下一个相同数字的位置

    if reverse:
        result.reverse()

    return result

def value_range_mapping_sort_parallel(nums, reverse=False):
    from concurrent.futures import ThreadPoolExecutor
    from collections import defaultdict

    if not nums:
        return []

    min_val, max_val = min(nums), max(nums)

    # 如果分布稀疏，则直接调用内置排序
    if max_val - min_val > len(nums) * 10:
        return sorted(nums, reverse=reverse)

    num_workers = 4
    chunk_size = len(nums) // num_workers + 1

    # 分块处理
    chunks = [nums[i:i + chunk_size] for i in range(0, len(nums), chunk_size)]

    # 局部计数器列表
    local_counts = []

    def count_chunk(chunk):
        count = defaultdict(int)
        for num in chunk:
            count[num] += 1
        return count

    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(count_chunk, chunk) for chunk in chunks]
        for future in futures:
            local_counts.append(future.result())

    # 合并局部计数器
    global_count = defaultdict(int)
    for count in local_counts:
        for key, val in count.items():
            global_count[key] += val

    # 构造结果
    result = []
    if reverse:
        for val in range(max_val, min_val - 1, -1):
            result.extend([val] * global_count.get(val, 0))
    else:
        for val in range(min_val, max_val + 1):
            result.extend([val] * global_count.get(val, 0))

    return result

def sort_help():
    print("可用的排序算法：")
    print("- quick_sort: 使用快速排序算法对数组进行排序。可通过 reverse 参数控制排序顺序（默认正序）")
    print("- shell_sort: 使用希尔排序算法对数组进行排序。可通过 reverse 参数控制排序顺序（默认正序）")
    print("- heap_sort: 使用堆排序算法对数组进行排序。可通过 reverse 参数控制排序顺序（默认正序）")
    print("- bucket_sort: 使用桶排序算法对数组进行排序。可通过 reverse 参数控制排序顺序（默认正序）")
    print("- insertion_sort: 使用插入排序算法对数组进行排序。可通过 reverse 参数控制排序顺序（默认正序）")
    print("- bubble_sort: 使用冒泡排序算法对数组进行排序。可通过 reverse 参数控制排序顺序（默认正序）")
    print("- merge_sort: 使用归并排序算法对数组进行排序。可通过 reverse 参数控制排序顺序（默认正序）")
    print("- selection_sort: 使用选择排序算法对数组进行排序。可通过 reverse 参数控制排序顺序（默认正序）")
    print("- counting_sort: 使用计数排序算法对数组进行排序。可通过 reverse 参数控制排序顺序（默认正序）")
    print("- radix_sort: 使用基数排序算法对数组进行排序。可通过 reverse 参数控制排序顺序（默认正序）")
    print("- value_range_mapping_sort: 使用值范围映射排序算法对数组进行排序。可通过 reverse 参数控制排序顺序（默认正序）")
    print("- value_range_mapping_sort_parallel: 使用并行值范围映射排序算法对数组进行排序。可通过 reverse 参数控制排序顺序（默认正序）")
    print("- sort_help: 显示可用的排序算法列表")