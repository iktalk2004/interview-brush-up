from django.core.management.base import BaseCommand
from apps.questions.models import Category, SubCategory, Question, CodeQuestionDetail


# 统一输入输出规范：
# - 输入：每行一个参数，数组用空格分隔
# - 输出：直接打印结果

CODE_QUESTIONS = [
    # ==================== 数组 ====================
    {
        'title': '两数之和',
        'sub_category': '数组与链表',
        'difficulty': 'easy',
        'description': '''给定一个整数数组 nums 和一个目标值 target，找出数组中和为目标值的两个整数的下标。

假设每种输入只有一个答案，且同一个元素不能使用两遍。

输入格式：
第一行：数组元素，空格分隔
第二行：目标值

输出格式：
两个下标，空格分隔（较小的在前）

示例：
输入：
2 7 11 15
9
输出：
0 1''',
        'test_cases': [
            {'input': '2 7 11 15\n9', 'output': '0 1'},
            {'input': '3 2 4\n6', 'output': '1 2'},
            {'input': '3 3\n6', 'output': '0 1'},
            {'input': '1 5 3 7 9\n12', 'output': '1 3'},
        ],
        'reference_code': '''nums = list(map(int, input().split()))
target = int(input())
d = {}
for i, n in enumerate(nums):
    if target - n in d:
        print(d[target-n], i)
        break
    d[n] = i''',
        'time_limit': 1000,
        'memory_limit': 256,
    },
    {
        'title': '最大子数组和',
        'sub_category': '数组与链表',
        'difficulty': 'medium',
        'description': '''给定一个整数数组 nums，找到具有最大和的连续子数组（至少包含一个元素），返回其最大和。

输入格式：
一行整数，空格分隔

输出格式：
最大子数组和

示例：
输入：
-2 1 -3 4 -1 2 1 -5 4
输出：
6''',
        'test_cases': [
            {'input': '-2 1 -3 4 -1 2 1 -5 4', 'output': '6'},
            {'input': '1', 'output': '1'},
            {'input': '5 4 -1 7 8', 'output': '23'},
            {'input': '-1 -2 -3', 'output': '-1'},
        ],
        'reference_code': '''nums = list(map(int, input().split()))
cur = res = nums[0]
for n in nums[1:]:
    cur = max(n, cur + n)
    res = max(res, cur)
print(res)''',
        'time_limit': 1000,
        'memory_limit': 256,
    },
    {
        'title': '合并两个有序数组',
        'sub_category': '数组与链表',
        'difficulty': 'easy',
        'description': '''给定两个有序整数数组 nums1 和 nums2，将 nums2 合并到 nums1 中，使结果有序。

输入格式：
第一行：nums1 的元素，空格分隔（若为空则输入 empty）
第二行：nums2 的元素，空格分隔（若为空则输入 empty）

输出格式：
合并后的有序数组，空格分隔

示例：
输入：
1 2 3
2 5 6
输出：
1 2 2 3 5 6''',
        'test_cases': [
            {'input': '1 2 3\n2 5 6', 'output': '1 2 2 3 5 6'},
            {'input': '1\nempty', 'output': '1'},
            {'input': 'empty\n1', 'output': '1'},
            {'input': '1 3 5 7\n2 4 6 8', 'output': '1 2 3 4 5 6 7 8'},
        ],
        'reference_code': '''a = input().strip()
b = input().strip()
nums1 = list(map(int, a.split())) if a != 'empty' else []
nums2 = list(map(int, b.split())) if b != 'empty' else []
result = sorted(nums1 + nums2)
print(' '.join(map(str, result)))''',
        'time_limit': 1000,
        'memory_limit': 256,
    },
    {
        'title': '移动零',
        'sub_category': '数组与链表',
        'difficulty': 'easy',
        'description': '''给定一个数组 nums，将所有 0 移动到数组末尾，同时保持非零元素的相对顺序。

输入格式：
一行整数，空格分隔

输出格式：
移动后的数组，空格分隔

示例：
输入：
0 1 0 3 12
输出：
1 3 12 0 0''',
        'test_cases': [
            {'input': '0 1 0 3 12', 'output': '1 3 12 0 0'},
            {'input': '0', 'output': '0'},
            {'input': '1 2 3', 'output': '1 2 3'},
            {'input': '0 0 1', 'output': '1 0 0'},
        ],
        'reference_code': '''nums = list(map(int, input().split()))
j = 0
for i in range(len(nums)):
    if nums[i] != 0:
        nums[j], nums[i] = nums[i], nums[j]
        j += 1
print(' '.join(map(str, nums)))''',
        'time_limit': 1000,
        'memory_limit': 256,
    },
    {
        'title': '盛最多水的容器',
        'sub_category': '数组与链表',
        'difficulty': 'medium',
        'description': '''给定 n 个非负整数 a1, a2, ..., an，每个数代表一条竖线的高度。找出两条线，使得它们与 x 轴共同构成的容器可以容纳最多的水。

输入格式：
一行整数，空格分隔

输出格式：
最多能容纳的水量

示例：
输入：
1 8 6 2 5 4 8 3 7
输出：
49''',
        'test_cases': [
            {'input': '1 8 6 2 5 4 8 3 7', 'output': '49'},
            {'input': '1 1', 'output': '1'},
            {'input': '4 3 2 1 4', 'output': '16'},
            {'input': '1 2 1', 'output': '2'},
        ],
        'reference_code': '''height = list(map(int, input().split()))
l, r = 0, len(height) - 1
res = 0
while l < r:
    res = max(res, min(height[l], height[r]) * (r - l))
    if height[l] < height[r]:
        l += 1
    else:
        r -= 1
print(res)''',
        'time_limit': 1000,
        'memory_limit': 256,
    },
    # ==================== 字符串 ====================
    {
        'title': '有效的括号',
        'sub_category': '数组与链表',
        'difficulty': 'easy',
        'description': '''给定一个只包括 '('，')'，'{'，'}'，'['，']' 的字符串 s，判断字符串是否有效。

输入格式：
一行字符串

输出格式：
true 或 false

示例：
输入：
()[]{}
输出：
true''',
        'test_cases': [
            {'input': '()[]{}', 'output': 'true'},
            {'input': '(]', 'output': 'false'},
            {'input': '{[]}', 'output': 'true'},
            {'input': '([)]', 'output': 'false'},
            {'input': '', 'output': 'true'},
        ],
        'reference_code': '''s = input().strip()
stack = []
m = {')':'(', '}':'{', ']':'['}
for c in s:
    if c in m:
        if not stack or stack[-1] != m[c]:
            print('false')
            exit()
        stack.pop()
    else:
        stack.append(c)
print('true' if not stack else 'false')''',
        'time_limit': 1000,
        'memory_limit': 256,
    },
    {
        'title': '最长无重复字符子串',
        'sub_category': '数组与链表',
        'difficulty': 'medium',
        'description': '''给定一个字符串 s，找出其中不含重复字符的最长子串的长度。

输入格式：
一行字符串

输出格式：
最长无重复子串的长度

示例：
输入：
abcabcbb
输出：
3''',
        'test_cases': [
            {'input': 'abcabcbb', 'output': '3'},
            {'input': 'bbbbb', 'output': '1'},
            {'input': 'pwwkew', 'output': '3'},
            {'input': '', 'output': '0'},
            {'input': 'abcdef', 'output': '6'},
        ],
        'reference_code': '''s = input().strip()
seen = {}
l = res = 0
for r, c in enumerate(s):
    if c in seen and seen[c] >= l:
        l = seen[c] + 1
    seen[c] = r
    res = max(res, r - l + 1)
print(res)''',
        'time_limit': 1000,
        'memory_limit': 256,
    },
    {
        'title': '字符串反转',
        'sub_category': '数组与链表',
        'difficulty': 'easy',
        'description': '''给定一个字符串 s，原地反转字符串。

输入格式：
一行字符串

输出格式：
反转后的字符串

示例：
输入：
hello
输出：
olleh''',
        'test_cases': [
            {'input': 'hello', 'output': 'olleh'},
            {'input': 'Hannah', 'output': 'hannaH'},
            {'input': 'a', 'output': 'a'},
            {'input': 'abcde', 'output': 'edcba'},
        ],
        'reference_code': '''print(input().strip()[::-1])''',
        'time_limit': 1000,
        'memory_limit': 256,
    },
    # ==================== 排序与搜索 ====================
    {
        'title': '二分查找',
        'sub_category': '排序算法',
        'difficulty': 'easy',
        'description': '''给定一个升序排列的整数数组 nums 和一个目标值 target，在数组中找到目标值并返回其索引。如果不存在，返回 -1。

输入格式：
第一行：数组元素，空格分隔
第二行：目标值

输出格式：
目标值的索引（不存在返回 -1）

示例：
输入：
-1 0 3 5 9 12
9
输出：
4''',
        'test_cases': [
            {'input': '-1 0 3 5 9 12\n9', 'output': '4'},
            {'input': '-1 0 3 5 9 12\n2', 'output': '-1'},
            {'input': '5\n5', 'output': '0'},
            {'input': '1 3 5 7 9\n7', 'output': '3'},
        ],
        'reference_code': '''nums = list(map(int, input().split()))
t = int(input())
l, r = 0, len(nums) - 1
ans = -1
while l <= r:
    m = (l + r) // 2
    if nums[m] == t:
        ans = m; break
    elif nums[m] < t:
        l = m + 1
    else:
        r = m - 1
print(ans)''',
        'time_limit': 1000,
        'memory_limit': 256,
    },
    {
        'title': '合并区间',
        'sub_category': '排序算法',
        'difficulty': 'medium',
        'description': '''给定一组区间，合并所有重叠的区间。

输入格式：
第一行：区间个数 n
接下来 n 行，每行两个整数表示区间的起止

输出格式：
合并后的区间，每行一个，两个整数空格分隔，按起点升序

示例：
输入：
4
1 3
2 6
8 10
15 18
输出：
1 6
8 10
15 18''',
        'test_cases': [
            {'input': '4\n1 3\n2 6\n8 10\n15 18', 'output': '1 6\n8 10\n15 18'},
            {'input': '2\n1 4\n4 5', 'output': '1 5'},
            {'input': '1\n1 1', 'output': '1 1'},
            {'input': '3\n1 4\n0 4\n3 5', 'output': '0 5'},
        ],
        'reference_code': '''n = int(input())
intervals = []
for _ in range(n):
    a, b = map(int, input().split())
    intervals.append([a, b])
intervals.sort()
merged = [intervals[0]]
for s, e in intervals[1:]:
    if s <= merged[-1][1]:
        merged[-1][1] = max(merged[-1][1], e)
    else:
        merged.append([s, e])
for a, b in merged:
    print(a, b)''',
        'time_limit': 1000,
        'memory_limit': 256,
    },
    {
        'title': '搜索旋转排序数组',
        'sub_category': '排序算法',
        'difficulty': 'medium',
        'description': '''一个升序排列的数组在某个点上进行了旋转（例如 [4,5,6,7,0,1,2]）。搜索一个给定的目标值，返回其索引，不存在返回 -1。要求时间复杂度 O(log n)。

输入格式：
第一行：数组元素，空格分隔
第二行：目标值

输出格式：
目标值的索引（不存在返回 -1）

示例：
输入：
4 5 6 7 0 1 2
0
输出：
4''',
        'test_cases': [
            {'input': '4 5 6 7 0 1 2\n0', 'output': '4'},
            {'input': '4 5 6 7 0 1 2\n3', 'output': '-1'},
            {'input': '1\n0', 'output': '-1'},
            {'input': '3 1\n1', 'output': '1'},
            {'input': '1 3\n3', 'output': '1'},
        ],
        'reference_code': '''nums = list(map(int, input().split()))
t = int(input())
l, r = 0, len(nums) - 1
ans = -1
while l <= r:
    m = (l + r) // 2
    if nums[m] == t:
        ans = m; break
    if nums[l] <= nums[m]:
        if nums[l] <= t < nums[m]:
            r = m - 1
        else:
            l = m + 1
    else:
        if nums[m] < t <= nums[r]:
            l = m + 1
        else:
            r = m - 1
print(ans)''',
        'time_limit': 1000,
        'memory_limit': 256,
    },
    # ==================== 动态规划 ====================
    {
        'title': '爬楼梯',
        'sub_category': '动态规划',
        'difficulty': 'easy',
        'description': '''假设你正在爬楼梯，需要 n 阶才能到达楼顶。每次可以爬 1 或 2 个台阶，共有多少种不同的方法？

输入格式：
一个整数 n

输出格式：
方法数

示例：
输入：
3
输出：
3''',
        'test_cases': [
            {'input': '2', 'output': '2'},
            {'input': '3', 'output': '3'},
            {'input': '5', 'output': '8'},
            {'input': '10', 'output': '89'},
        ],
        'reference_code': '''n = int(input())
if n <= 2:
    print(n)
else:
    a, b = 1, 2
    for _ in range(3, n + 1):
        a, b = b, a + b
    print(b)''',
        'time_limit': 1000,
        'memory_limit': 256,
    },
    {
        'title': '零钱兑换',
        'sub_category': '动态规划',
        'difficulty': 'medium',
        'description': '''给定不同面额的硬币 coins 和一个总金额 amount，计算可以凑成总金额所需的最少硬币个数。如果无法凑成，返回 -1。

输入格式：
第一行：硬币面额，空格分隔
第二行：总金额

输出格式：
最少硬币数（无法凑成返回 -1）

示例：
输入：
1 2 5
11
输出：
3''',
        'test_cases': [
            {'input': '1 2 5\n11', 'output': '3'},
            {'input': '2\n3', 'output': '-1'},
            {'input': '1\n0', 'output': '0'},
            {'input': '1 2 5\n100', 'output': '20'},
            {'input': '2 5 10 1\n27', 'output': '4'},
        ],
        'reference_code': '''coins = list(map(int, input().split()))
amount = int(input())
dp = [float('inf')] * (amount + 1)
dp[0] = 0
for i in range(1, amount + 1):
    for c in coins:
        if c <= i and dp[i - c] + 1 < dp[i]:
            dp[i] = dp[i - c] + 1
print(dp[amount] if dp[amount] != float('inf') else -1)''',
        'time_limit': 2000,
        'memory_limit': 256,
    },
    {
        'title': '最长递增子序列',
        'sub_category': '动态规划',
        'difficulty': 'medium',
        'description': '''给定一个整数数组 nums，找到其中最长严格递增子序列的长度。

输入格式：
一行整数，空格分隔

输出格式：
最长递增子序列的长度

示例：
输入：
10 9 2 5 3 7 101 18
输出：
4''',
        'test_cases': [
            {'input': '10 9 2 5 3 7 101 18', 'output': '4'},
            {'input': '0 1 0 3 2 3', 'output': '4'},
            {'input': '7 7 7 7 7', 'output': '1'},
            {'input': '1 2 3 4 5', 'output': '5'},
        ],
        'reference_code': '''import bisect
nums = list(map(int, input().split()))
tails = []
for n in nums:
    pos = bisect.bisect_left(tails, n)
    if pos == len(tails):
        tails.append(n)
    else:
        tails[pos] = n
print(len(tails))''',
        'time_limit': 1000,
        'memory_limit': 256,
    },
    {
        'title': '打家劫舍',
        'sub_category': '动态规划',
        'difficulty': 'medium',
        'description': '''你是一个专业的小偷，沿街有一排房屋。每间房内都有一定的现金，但相邻的房屋装有相互连通的防盗系统，如果两间相邻的房屋在同一晚上被小偷闯入，系统会自动报警。

给定一个代表每间房屋金额的数组，计算不触动警报的情况下能够偷窃到的最高金额。

输入格式：
一行整数，空格分隔

输出格式：
最高金额

示例：
输入：
1 2 3 1
输出：
4''',
        'test_cases': [
            {'input': '1 2 3 1', 'output': '4'},
            {'input': '2 7 9 3 1', 'output': '12'},
            {'input': '2 1 1 2', 'output': '4'},
            {'input': '100', 'output': '100'},
        ],
        'reference_code': '''nums = list(map(int, input().split()))
if len(nums) <= 2:
    print(max(nums))
else:
    a, b = nums[0], max(nums[0], nums[1])
    for i in range(2, len(nums)):
        a, b = b, max(b, a + nums[i])
    print(b)''',
        'time_limit': 1000,
        'memory_limit': 256,
    },
    # ==================== 树与图 ====================
    {
        'title': '二叉树的最大深度',
        'sub_category': '树与图',
        'difficulty': 'easy',
        'description': '''给定一棵二叉树（层序遍历表示，null 表示空节点），求其最大深度。

输入格式：
一行，节点值空格分隔，null 表示空节点（层序遍历）

输出格式：
最大深度

示例：
输入：
3 9 20 null null 15 7
输出：
3''',
        'test_cases': [
            {'input': '3 9 20 null null 15 7', 'output': '3'},
            {'input': '1 null 2', 'output': '2'},
            {'input': '1', 'output': '1'},
            {'input': '1 2 3 4 5', 'output': '3'},
        ],
        'reference_code': '''from collections import deque
vals = input().split()
if not vals or vals[0] == 'null':
    print(0)
else:
    nodes = [None if v == 'null' else int(v) for v in vals]
    # BFS 计算深度
    depth = 0
    q = deque([0])
    while q:
        depth += 1
        for _ in range(len(q)):
            i = q.popleft()
            l, r = 2*i+1, 2*i+2
            if l < len(nodes) and nodes[l] is not None:
                q.append(l)
            if r < len(nodes) and nodes[r] is not None:
                q.append(r)
    print(depth)''',
        'time_limit': 1000,
        'memory_limit': 256,
    },
    {
        'title': '对称二叉树',
        'sub_category': '树与图',
        'difficulty': 'easy',
        'description': '''给定一棵二叉树（层序遍历表示），检查它是否是镜像对称的。

输入格式：
一行，节点值空格分隔，null 表示空节点

输出格式：
true 或 false

示例：
输入：
1 2 2 3 4 4 3
输出：
true''',
        'test_cases': [
            {'input': '1 2 2 3 4 4 3', 'output': 'true'},
            {'input': '1 2 2 null 3 null 3', 'output': 'false'},
            {'input': '1', 'output': 'true'},
            {'input': '1 2 2', 'output': 'true'},
        ],
        'reference_code': '''vals = input().split()
nodes = [None if v == 'null' else int(v) for v in vals]
n = len(nodes)
def get(i):
    return nodes[i] if i < n else None
def check(i, j):
    a, b = get(i), get(j)
    if a is None and b is None: return True
    if a is None or b is None: return False
    if a != b: return False
    return check(2*i+1, 2*j+2) and check(2*i+2, 2*j+1)
print('true' if check(1, 2) else 'false')''',
        'time_limit': 1000,
        'memory_limit': 256,
    },
    # ==================== 栈与队列 ====================
    {
        'title': '用栈实现队列',
        'sub_category': '数组与链表',
        'difficulty': 'easy',
        'description': '''使用两个栈实现先入先出队列。支持以下操作：
- push x：将元素 x 推到队列末尾
- pop：移除并返回队列开头的元素
- peek：返回队列开头的元素

输入格式：
第一行：操作个数 n
接下来 n 行，每行一个操作

输出格式：
对于 pop 和 peek 操作，每行输出一个结果

示例：
输入：
5
push 1
push 2
peek
pop
peek
输出：
1
1
2''',
        'test_cases': [
            {'input': '5\npush 1\npush 2\npeek\npop\npeek', 'output': '1\n1\n2'},
            {'input': '4\npush 10\npush 20\npop\npop', 'output': '10\n20'},
            {'input': '3\npush 5\npeek\npop', 'output': '5\n5'},
        ],
        'reference_code': '''n = int(input())
s1, s2 = [], []
results = []
for _ in range(n):
    op = input().split()
    if op[0] == 'push':
        s1.append(int(op[1]))
    elif op[0] == 'pop':
        if not s2:
            while s1:
                s2.append(s1.pop())
        results.append(str(s2.pop()))
    elif op[0] == 'peek':
        if not s2:
            while s1:
                s2.append(s1.pop())
        results.append(str(s2[-1]))
print('\\n'.join(results))''',
        'time_limit': 1000,
        'memory_limit': 256,
    },
    # ==================== 哈希 / 双指针 ====================
    {
        'title': '两数之和 II（有序数组）',
        'sub_category': '数组与链表',
        'difficulty': 'medium',
        'description': '''给定一个已按升序排列的整数数组 numbers 和目标值 target，找出两个数的下标（1-indexed）使其和等于目标值。

输入格式：
第一行：数组元素，空格分隔
第二行：目标值

输出格式：
两个下标（1-indexed），空格分隔

示例：
输入：
2 7 11 15
9
输出：
1 2''',
        'test_cases': [
            {'input': '2 7 11 15\n9', 'output': '1 2'},
            {'input': '2 3 4\n6', 'output': '1 3'},
            {'input': '-1 0\n-1', 'output': '1 2'},
            {'input': '1 2 3 4 5\n9', 'output': '4 5'},
        ],
        'reference_code': '''nums = list(map(int, input().split()))
t = int(input())
l, r = 0, len(nums) - 1
while l < r:
    s = nums[l] + nums[r]
    if s == t:
        print(l + 1, r + 1)
        break
    elif s < t:
        l += 1
    else:
        r -= 1''',
        'time_limit': 1000,
        'memory_limit': 256,
    },
    {
        'title': '三数之和',
        'sub_category': '数组与链表',
        'difficulty': 'medium',
        'description': '''给定一个整数数组 nums，找出所有不重复的三元组 [a, b, c] 使得 a + b + c = 0。结果按升序排列。

输入格式：
一行整数，空格分隔

输出格式：
每行一个三元组，空格分隔，按字典序排列。若无解输出 none。

示例：
输入：
-1 0 1 2 -1 -4
输出：
-1 -1 2
-1 0 1''',
        'test_cases': [
            {'input': '-1 0 1 2 -1 -4', 'output': '-1 -1 2\n-1 0 1'},
            {'input': '0 0 0', 'output': '0 0 0'},
            {'input': '1 2 3', 'output': 'none'},
            {'input': '-2 0 1 1 2', 'output': '-2 0 2\n-2 1 1'},
        ],
        'reference_code': '''nums = sorted(map(int, input().split()))
n = len(nums)
res = []
for i in range(n - 2):
    if i > 0 and nums[i] == nums[i-1]: continue
    l, r = i + 1, n - 1
    while l < r:
        s = nums[i] + nums[l] + nums[r]
        if s == 0:
            res.append(f'{nums[i]} {nums[l]} {nums[r]}')
            while l < r and nums[l] == nums[l+1]: l += 1
            while l < r and nums[r] == nums[r-1]: r -= 1
            l += 1; r -= 1
        elif s < 0:
            l += 1
        else:
            r -= 1
print('\\n'.join(res) if res else 'none')''',
        'time_limit': 2000,
        'memory_limit': 256,
    },
    # ==================== 回溯 ====================
    {
        'title': '全排列',
        'sub_category': '排序算法',
        'difficulty': 'medium',
        'description': '''给定一个不含重复数字的数组 nums，返回其所有可能的全排列，按字典序排列。

输入格式：
一行整数，空格分隔

输出格式：
每行一个排列，数字空格分隔

示例：
输入：
1 2 3
输出：
1 2 3
1 3 2
2 1 3
2 3 1
3 1 2
3 2 1''',
        'test_cases': [
            {'input': '1 2 3', 'output': '1 2 3\n1 3 2\n2 1 3\n2 3 1\n3 1 2\n3 2 1'},
            {'input': '0 1', 'output': '0 1\n1 0'},
            {'input': '1', 'output': '1'},
        ],
        'reference_code': '''nums = sorted(map(int, input().split()))
res = []
def bt(path, remain):
    if not remain:
        res.append(' '.join(map(str, path)))
        return
    for i in range(len(remain)):
        bt(path + [remain[i]], remain[:i] + remain[i+1:])
bt([], nums)
print('\\n'.join(res))''',
        'time_limit': 2000,
        'memory_limit': 256,
    },
    # ==================== 贪心 ====================
    {
        'title': '买卖股票的最佳时机',
        'sub_category': '动态规划',
        'difficulty': 'easy',
        'description': '''给定一个数组 prices，其中 prices[i] 是股票第 i 天的价格。你只能选择某一天买入并在之后的某一天卖出，计算你所能获取的最大利润。如果无法获利，返回 0。

输入格式：
一行整数，空格分隔

输出格式：
最大利润

示例：
输入：
7 1 5 3 6 4
输出：
5''',
        'test_cases': [
            {'input': '7 1 5 3 6 4', 'output': '5'},
            {'input': '7 6 4 3 1', 'output': '0'},
            {'input': '2 4 1', 'output': '2'},
            {'input': '1 2', 'output': '1'},
        ],
        'reference_code': '''prices = list(map(int, input().split()))
min_p = prices[0]
res = 0
for p in prices[1:]:
    res = max(res, p - min_p)
    min_p = min(min_p, p)
print(res)''',
        'time_limit': 1000,
        'memory_limit': 256,
    },
    {
        'title': '跳跃游戏',
        'sub_category': '动态规划',
        'difficulty': 'medium',
        'description': '''给定一个非负整数数组 nums，每个元素代表你在该位置可以跳跃的最大长度。判断你是否能够到达最后一个下标。

输入格式：
一行整数，空格分隔

输出格式：
true 或 false

示例：
输入：
2 3 1 1 4
输出：
true''',
        'test_cases': [
            {'input': '2 3 1 1 4', 'output': 'true'},
            {'input': '3 2 1 0 4', 'output': 'false'},
            {'input': '0', 'output': 'true'},
            {'input': '2 0 0', 'output': 'true'},
            {'input': '1 1 1 1', 'output': 'true'},
        ],
        'reference_code': '''nums = list(map(int, input().split()))
reach = 0
for i in range(len(nums)):
    if i > reach:
        print('false')
        exit()
    reach = max(reach, i + nums[i])
print('true')''',
        'time_limit': 1000,
        'memory_limit': 256,
    },
    # ==================== 困难题 ====================
    {
        'title': '接雨水',
        'sub_category': '数组与链表',
        'difficulty': 'hard',
        'description': '''给定 n 个非负整数表示每个宽度为 1 的柱子的高度图，计算下雨之后能接多少雨水。

输入格式：
一行整数，空格分隔

输出格式：
能接的雨水总量

示例：
输入：
0 1 0 2 1 0 1 3 2 1 2 1
输出：
6''',
        'test_cases': [
            {'input': '0 1 0 2 1 0 1 3 2 1 2 1', 'output': '6'},
            {'input': '4 2 0 3 2 5', 'output': '9'},
            {'input': '1 2 3', 'output': '0'},
            {'input': '3 0 3', 'output': '3'},
        ],
        'reference_code': '''h = list(map(int, input().split()))
n = len(h)
if n < 3:
    print(0)
else:
    l, r = 0, n - 1
    lmax = rmax = 0
    res = 0
    while l < r:
        if h[l] < h[r]:
            lmax = max(lmax, h[l])
            res += lmax - h[l]
            l += 1
        else:
            rmax = max(rmax, h[r])
            res += rmax - h[r]
            r -= 1
    print(res)''',
        'time_limit': 1000,
        'memory_limit': 256,
    },
]


class Command(BaseCommand):
    help = '导入代码题（含测试用例）'

    def handle(self, *args, **options):
        self.stdout.write('开始导入代码题...')

        cat_algo = Category.objects.filter(name='数据结构与算法').first()
        if not cat_algo:
            self.stdout.write(self.style.ERROR('未找到"数据结构与算法"分类，请先运行 seed_data'))
            return

        created = 0
        updated = 0

        for item in CODE_QUESTIONS:
            sub = SubCategory.objects.filter(
                category=cat_algo, name=item['sub_category']
            ).first()
            if not sub:
                self.stdout.write(f"  跳过：子分类 {item['sub_category']} 不存在")
                continue

            q, is_new = Question.objects.get_or_create(
                title=item['title'],
                defaults={
                    'question_type': 'code',
                    'category': cat_algo,
                    'sub_category': sub,
                    'difficulty': item['difficulty'],
                }
            )

            if is_new:
                CodeQuestionDetail.objects.create(
                    question=q,
                    description=item['description'],
                    test_cases=item['test_cases'],
                    reference_code=item['reference_code'],
                    time_limit=item.get('time_limit', 1000),
                    memory_limit=item.get('memory_limit', 256),
                )
                created += 1
            else:
                # 更新已有题目的测试用例和描述
                detail = q.code_detail
                if detail:
                    detail.description = item['description']
                    detail.test_cases = item['test_cases']
                    detail.reference_code = item['reference_code']
                    detail.time_limit = item.get('time_limit', 1000)
                    detail.memory_limit = item.get('memory_limit', 256)
                    detail.save()
                    updated += 1

        self.stdout.write(self.style.SUCCESS(
            f'代码题导入完成！新增 {created} 道，更新 {updated} 道，总计 {Question.objects.filter(question_type="code").count()} 道代码题'
        ))