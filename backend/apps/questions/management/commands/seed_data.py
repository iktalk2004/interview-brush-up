import random
import math
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from apps.users.models import User, UserInterest
from apps.questions.models import Category, SubCategory, Question, TextQuestionDetail, CodeQuestionDetail
from apps.practice.models import SubmissionRecord, UserQuestionStatus
from apps.announcements.models import Announcement


class Command(BaseCommand):
    help = '填充模拟数据（含偏好模式）'

    # 用户群组定义：每组用户偏好相似的分类
    USER_PROFILES = [
        {
            'prefix': 'backend',
            'count': 6,
            'primary': ['Python后端', '数据库'],
            'secondary': ['操作系统', '设计模式'],
            'level': 'intermediate',
        },
        {
            'prefix': 'frontend',
            'count': 5,
            'primary': ['前端开发', 'JavaScript基础'],
            'secondary': ['计算机网络', 'Python后端'],
            'level': 'intermediate',
        },
        {
            'prefix': 'algo',
            'count': 5,
            'primary': ['数据结构与算法'],
            'secondary': ['操作系统', '计算机网络'],
            'level': 'advanced',
        },
        {
            'prefix': 'fullstack',
            'count': 4,
            'primary': ['Python后端', '前端开发', '数据库'],
            'secondary': ['计算机网络', '数据结构与算法'],
            'level': 'advanced',
        },
        {
            'prefix': 'beginner',
            'count': 5,
            'primary': ['计算机网络', '操作系统'],
            'secondary': ['数据库'],
            'level': 'beginner',
        },
    ]

    def handle(self, *args, **options):
        self.stdout.write('开始填充模拟数据（含偏好模式）...')

        self._create_categories()
        self._create_questions()
        self._create_users()
        self._create_submissions()
        self._create_announcements()
        self._compute_similarities()

        self.stdout.write(self.style.SUCCESS('模拟数据填充完成！'))

    def _create_categories(self):
        self.stdout.write('创建分类...')

        data = {
            'Python后端': ['Django', 'Flask', 'FastAPI', 'Python基础'],
            '计算机网络': ['TCP/IP', 'HTTP', 'DNS与CDN', '网络安全'],
            '操作系统': ['进程与线程', '内存管理', '文件系统', 'Linux'],
            '数据库': ['MySQL', 'Redis', '索引优化', '事务与锁'],
            '数据结构与算法': ['数组与链表', '树与图', '排序算法', '动态规划'],
            '前端开发': ['JavaScript', 'Vue.js', 'CSS布局', '浏览器原理'],
            'Java后端': ['Spring Boot', 'JVM', 'Java集合', '并发编程'],
            '设计模式': ['创建型模式', '结构型模式', '行为型模式'],
        }

        for idx, (cat_name, subs) in enumerate(data.items()):
            cat, _ = Category.objects.get_or_create(
                name=cat_name,
                defaults={'description': f'{cat_name}相关知识', 'sort_order': idx}
            )
            for sub_idx, sub_name in enumerate(subs):
                SubCategory.objects.get_or_create(
                    category=cat, name=sub_name,
                    defaults={'sort_order': sub_idx}
                )

        self.stdout.write(f'  分类: {Category.objects.count()} 个，子分类: {SubCategory.objects.count()} 个')

    def _create_questions(self):
        self.stdout.write('创建题目...')

        # 为每个子分类批量生成简答题
        question_templates = {
            'Django': [
                ('请解释Django的MTV架构', 'easy'),
                ('Django中间件的执行顺序是什么', 'medium'),
                ('DRF序列化器的作用是什么', 'easy'),
                ('Django ORM的N+1查询问题如何解决', 'hard'),
                ('Django的信号机制是什么', 'medium'),
                ('Django中如何实现数据库读写分离', 'hard'),
            ],
            'Flask': [
                ('Flask和Django的主要区别是什么', 'easy'),
                ('Flask的应用上下文和请求上下文的区别', 'medium'),
                ('Flask蓝图的作用是什么', 'easy'),
                ('Flask中如何处理跨域请求', 'medium'),
            ],
            'FastAPI': [
                ('FastAPI相比Flask有什么优势', 'easy'),
                ('FastAPI中的依赖注入机制', 'medium'),
                ('FastAPI如何实现异步请求处理', 'medium'),
            ],
            'Python基础': [
                ('Python中的GIL是什么', 'medium'),
                ('Python装饰器的工作原理', 'medium'),
                ('解释Python的深拷贝和浅拷贝', 'easy'),
                ('Python生成器和迭代器的区别', 'medium'),
                ('Python中的metaclass是什么', 'hard'),
                ('Python的垃圾回收机制', 'medium'),
                ('Python多线程和多进程的区别', 'medium'),
            ],
            'TCP/IP': [
                ('TCP三次握手的过程', 'easy'),
                ('TCP和UDP的区别', 'easy'),
                ('TCP的拥塞控制机制', 'hard'),
                ('TCP四次挥手的过程', 'medium'),
                ('TCP滑动窗口的作用', 'medium'),
                ('IP地址的分类方式', 'easy'),
            ],
            'HTTP': [
                ('HTTP和HTTPS的区别', 'easy'),
                ('HTTP/2相比HTTP/1.1有哪些改进', 'medium'),
                ('常见的HTTP状态码及含义', 'easy'),
                ('HTTP请求方法GET和POST的区别', 'easy'),
                ('Cookie和Session的区别', 'medium'),
                ('RESTful API设计规范', 'medium'),
            ],
            'DNS与CDN': [
                ('DNS解析的过程', 'medium'),
                ('CDN的工作原理', 'medium'),
                ('DNS劫持和DNS污染的区别', 'hard'),
            ],
            '网络安全': [
                ('什么是XSS攻击及如何防范', 'medium'),
                ('什么是CSRF攻击及如何防范', 'medium'),
                ('SQL注入的原理和防范方法', 'medium'),
                ('什么是CORS', 'easy'),
            ],
            '进程与线程': [
                ('进程和线程的区别', 'easy'),
                ('死锁的四个必要条件', 'medium'),
                ('进程间通信的方式有哪些', 'medium'),
                ('什么是协程', 'medium'),
                ('线程同步的方式有哪些', 'medium'),
            ],
            '内存管理': [
                ('虚拟内存的作用是什么', 'medium'),
                ('页面置换算法有哪些', 'medium'),
                ('内存泄漏和内存溢出的区别', 'easy'),
                ('什么是内存碎片', 'medium'),
            ],
            '文件系统': [
                ('硬链接和软链接的区别', 'medium'),
                ('常见的文件系统有哪些', 'easy'),
                ('inode是什么', 'medium'),
            ],
            'Linux': [
                ('常用的Linux命令有哪些', 'easy'),
                ('Linux文件权限的表示方式', 'easy'),
                ('Linux中的管道和重定向', 'medium'),
                ('crontab的使用方法', 'medium'),
            ],
            'MySQL': [
                ('MySQL的InnoDB和MyISAM的区别', 'medium'),
                ('MySQL索引的底层数据结构', 'hard'),
                ('MySQL事务的ACID特性', 'medium'),
                ('MySQL主从复制的原理', 'hard'),
                ('EXPLAIN命令的使用方法', 'medium'),
                ('MySQL慢查询优化方法', 'medium'),
            ],
            'Redis': [
                ('Redis的常用数据类型有哪些', 'easy'),
                ('Redis的持久化方式有哪些', 'medium'),
                ('Redis缓存穿透、击穿、雪崩的区别', 'hard'),
                ('Redis的过期策略和淘汰策略', 'medium'),
                ('Redis实现分布式锁的方式', 'hard'),
            ],
            '索引优化': [
                ('什么是最左前缀原则', 'medium'),
                ('聚簇索引和非聚簇索引的区别', 'medium'),
                ('什么是覆盖索引', 'medium'),
                ('什么情况下索引会失效', 'medium'),
            ],
            '事务与锁': [
                ('数据库事务的隔离级别', 'medium'),
                ('乐观锁和悲观锁的区别', 'medium'),
                ('MVCC的工作原理', 'hard'),
            ],
            '数组与链表': [
                ('数组和链表的区别', 'easy'),
                ('如何判断链表有环', 'medium'),
                ('LRU缓存的实现方式', 'hard'),
                ('如何合并两个有序数组', 'easy'),
            ],
            '树与图': [
                ('二叉树的遍历方式', 'easy'),
                ('平衡二叉树和红黑树的区别', 'hard'),
                ('B树和B+树的区别', 'medium'),
                ('图的BFS和DFS', 'medium'),
            ],
            '排序算法': [
                ('快速排序的原理和时间复杂度', 'medium'),
                ('归并排序和快速排序的比较', 'medium'),
                ('堆排序的原理', 'medium'),
                ('各排序算法的稳定性比较', 'easy'),
            ],
            '动态规划': [
                ('动态规划和贪心算法的区别', 'hard'),
                ('最长公共子序列问题', 'medium'),
                ('背包问题的解法', 'hard'),
                ('动态规划的状态转移方程如何设计', 'hard'),
            ],
            'JavaScript': [
                ('JavaScript中的闭包是什么', 'medium'),
                ('Promise和async/await的关系', 'medium'),
                ('原型链的工作原理', 'medium'),
                ('事件循环机制', 'hard'),
                ('var/let/const的区别', 'easy'),
                ('箭头函数和普通函数的区别', 'easy'),
            ],
            'Vue.js': [
                ('Vue3的Composition API和Options API的区别', 'medium'),
                ('Vue的响应式原理', 'hard'),
                ('Vue组件通信的方式有哪些', 'medium'),
                ('Vue的虚拟DOM和diff算法', 'hard'),
                ('Vue Router的导航守卫', 'medium'),
                ('Vuex和Pinia的区别', 'easy'),
            ],
            'CSS布局': [
                ('Flex布局和Grid布局的区别', 'easy'),
                ('CSS盒模型的理解', 'easy'),
                ('BFC是什么', 'medium'),
                ('CSS选择器的优先级', 'easy'),
            ],
            '浏览器原理': [
                ('浏览器渲染页面的流程', 'medium'),
                ('重排和重绘的区别', 'medium'),
                ('浏览器的缓存机制', 'medium'),
                ('从输入URL到页面展示的全过程', 'hard'),
            ],
            'Spring Boot': [
                ('Spring Boot自动配置的原理', 'medium'),
                ('Spring IOC和AOP的理解', 'medium'),
                ('Spring Bean的生命周期', 'hard'),
                ('Spring事务的传播机制', 'hard'),
            ],
            'JVM': [
                ('JVM内存模型', 'medium'),
                ('JVM垃圾回收算法', 'medium'),
                ('类加载机制', 'medium'),
                ('JVM调优的方法', 'hard'),
            ],
            'Java集合': [
                ('HashMap的底层原理', 'medium'),
                ('ArrayList和LinkedList的区别', 'easy'),
                ('ConcurrentHashMap的实现原理', 'hard'),
                ('HashMap和Hashtable的区别', 'easy'),
            ],
            '并发编程': [
                ('synchronized和ReentrantLock的区别', 'medium'),
                ('线程池的核心参数', 'medium'),
                ('volatile关键字的作用', 'medium'),
                ('CAS的原理', 'hard'),
            ],
            '创建型模式': [
                ('单例模式的实现方式', 'easy'),
                ('工厂模式和抽象工厂模式的区别', 'medium'),
                ('建造者模式的应用场景', 'medium'),
            ],
            '结构型模式': [
                ('适配器模式和装饰器模式的区别', 'medium'),
                ('代理模式的应用场景', 'medium'),
                ('什么是外观模式', 'easy'),
            ],
            '行为型模式': [
                ('观察者模式的应用场景', 'medium'),
                ('策略模式和状态模式的区别', 'medium'),
                ('什么是责任链模式', 'medium'),
            ],
        }

        # 生成标准答案模板
        answer_templates = {
            'easy': ('这是一个基础概念题。核心要点包括：定义、特点、适用场景。', '这是基础知识点，理解概念即可。'),
            'medium': ('这是一个中等难度题。需要理解原理和实现机制，包括：工作流程、核心组件、优缺点对比。', '建议结合实际项目经验来理解。'),
            'hard': ('这是一道高难度题。需要深入理解底层实现，包括：数据结构选择、算法复杂度分析、边界情况处理、性能优化策略。', '这是高级知识点，建议深入阅读源码和论文。'),
        }

        count = 0
        for sub_name, questions in question_templates.items():
            try:
                sub = SubCategory.objects.filter(name=sub_name).first()
                if not sub:
                    continue
            except Exception:
                continue

            for title, diff in questions:
                q, created = Question.objects.get_or_create(
                    title=title,
                    defaults={
                        'question_type': 'text',
                        'category': sub.category,
                        'sub_category': sub,
                        'difficulty': diff,
                    }
                )
                if created:
                    answer, explanation = answer_templates[diff]
                    TextQuestionDetail.objects.create(
                        question=q,
                        standard_answer=f'{title}的标准答案：{answer}',
                        explanation=explanation,
                    )
                    count += 1

        # 代码题
        code_questions = [
            ('两数之和', 'easy', '数据结构与算法', '数组与链表',
             '给定一个整数数组nums和一个目标值target，请找出和为目标值的两个整数的下标。',
             [{'input': '[2,7,11,15]\n9', 'output': '[0,1]'}],
             'def twoSum(nums, target):\n    d = {}\n    for i, n in enumerate(nums):\n        if target-n in d: return [d[target-n], i]\n        d[n] = i'),
            ('反转链表', 'easy', '数据结构与算法', '数组与链表',
             '给你单链表的头节点head，请你反转链表。',
             [{'input': '[1,2,3,4,5]', 'output': '[5,4,3,2,1]'}],
             'def reverseList(head):\n    prev=None\n    while head:\n        nxt=head.next; head.next=prev; prev=head; head=nxt\n    return prev'),
            ('有效的括号', 'easy', '数据结构与算法', '数组与链表',
             '判断只包括(){}[]的字符串是否有效。',
             [{'input': '()', 'output': 'true'}, {'input': '(]', 'output': 'false'}],
             'def isValid(s):\n    stack=[]\n    m={")":"(","}":"{","]":"["}\n    for c in s:\n        if c in m:\n            if not stack or stack[-1]!=m[c]: return False\n            stack.pop()\n        else: stack.append(c)\n    return not stack'),
            ('二分查找', 'easy', '数据结构与算法', '排序算法',
             '在排序数组中找到目标值并返回索引，不存在返回-1。',
             [{'input': '[-1,0,3,5,9,12]\n9', 'output': '4'}],
             'def search(nums,t):\n    l,r=0,len(nums)-1\n    while l<=r:\n        m=(l+r)//2\n        if nums[m]==t: return m\n        elif nums[m]<t: l=m+1\n        else: r=m-1\n    return -1'),
            ('爬楼梯', 'medium', '数据结构与算法', '动态规划',
             '需要n阶到楼顶，每次可爬1或2阶，有多少种方法？',
             [{'input': '2', 'output': '2'}, {'input': '3', 'output': '3'}],
             'def climbStairs(n):\n    if n<=2: return n\n    a,b=1,2\n    for _ in range(3,n+1): a,b=b,a+b\n    return b'),
            ('最大子数组和', 'medium', '数据结构与算法', '动态规划',
             '找到具有最大和的连续子数组并返回其最大和。',
             [{'input': '[-2,1,-3,4,-1,2,1,-5,4]', 'output': '6'}],
             'def maxSubArray(nums):\n    cur=res=nums[0]\n    for n in nums[1:]:\n        cur=max(n,cur+n)\n        res=max(res,cur)\n    return res'),
        ]

        for title, diff, cat_name, sub_name, desc, cases, code in code_questions:
            cat = Category.objects.get(name=cat_name)
            sub = SubCategory.objects.get(category=cat, name=sub_name)
            q, created = Question.objects.get_or_create(
                title=title,
                defaults={'question_type': 'code', 'category': cat, 'sub_category': sub, 'difficulty': diff}
            )
            if created:
                CodeQuestionDetail.objects.create(question=q, description=desc, test_cases=cases, reference_code=code)
                count += 1

        self.stdout.write(f'  新增题目: {count} 道，总题目: {Question.objects.count()} 道')

    def _create_users(self):
        self.stdout.write('创建模拟用户...')
        educations = ['bachelor', 'master', 'associate']
        created = 0

        for profile in self.USER_PROFILES:
            for i in range(1, profile['count'] + 1):
                username = f"{profile['prefix']}{i:02d}"
                user, is_new = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': f'{username}@test.com',
                        'tech_level': profile['level'],
                        'education': random.choice(educations),
                    }
                )
                if is_new:
                    user.set_password('test123456')
                    user.save()
                    all_interests = profile['primary'] + profile['secondary']
                    for interest in all_interests:
                        try:
                            UserInterest.objects.create(user=user, category_name=interest)
                        except Exception:
                            pass
                    created += 1

        self.stdout.write(f'  新增用户: {created} 个，总用户: {User.objects.count()} 个')

    def _create_submissions(self):
        self.stdout.write('创建模拟答题记录（带偏好模式）...')

        now = timezone.now()
        all_questions = list(Question.objects.filter(question_type='text'))
        if not all_questions:
            return

        # 按分类组织题目
        cat_questions = {}
        for q in all_questions:
            cat_name = q.category.name
            if cat_name not in cat_questions:
                cat_questions[cat_name] = []
            cat_questions[cat_name].append(q)

        created = 0

        for profile in self.USER_PROFILES:
            for i in range(1, profile['count'] + 1):
                username = f"{profile['prefix']}{i:02d}"
                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    continue

                # 选择该用户会做的题目
                selected = []

                # 主要兴趣分类：做70-90%的题
                for cat_name in profile['primary']:
                    if cat_name in cat_questions:
                        qs = cat_questions[cat_name]
                        ratio = random.uniform(0.7, 0.9)
                        count = max(1, int(len(qs) * ratio))
                        selected.extend(random.sample(qs, min(count, len(qs))))

                # 次要兴趣分类：做30-50%的题
                for cat_name in profile['secondary']:
                    if cat_name in cat_questions:
                        qs = cat_questions[cat_name]
                        ratio = random.uniform(0.3, 0.5)
                        count = max(1, int(len(qs) * ratio))
                        selected.extend(random.sample(qs, min(count, len(qs))))

                # 随机做少量其他分类的题（10-20%）
                other_cats = [c for c in cat_questions if c not in profile['primary'] and c not in profile['secondary']]
                for cat_name in other_cats:
                    if random.random() < 0.3:
                        qs = cat_questions[cat_name]
                        count = max(1, int(len(qs) * random.uniform(0.1, 0.2)))
                        selected.extend(random.sample(qs, min(count, len(qs))))

                # 去重
                selected = list({q.id: q for q in selected}.values())

                for q in selected:
                    # 主要兴趣的题得分更高
                    is_primary = q.category.name in profile['primary']
                    is_secondary = q.category.name in profile['secondary']

                    if is_primary:
                        base_score = random.uniform(60, 95)
                    elif is_secondary:
                        base_score = random.uniform(40, 85)
                    else:
                        base_score = random.uniform(20, 70)

                    # 难度影响
                    if q.difficulty == 'hard':
                        base_score *= 0.8
                    elif q.difficulty == 'easy':
                        base_score = min(100, base_score * 1.1)

                    score = round(min(100, max(0, base_score)), 2)
                    days_ago = random.randint(0, 13)
                    created_at = now - timedelta(days=days_ago, hours=random.randint(0, 23))

                    record = SubmissionRecord(
                        user=user, question=q,
                        user_answer=f'模拟答案',
                        score=score, is_correct=score >= 60,
                        scoring_method=random.choice(['model', 'deepseek']),
                        time_spent=random.randint(30, 300),
                        ai_feedback='模拟评语',
                        created_at=created_at,
                    )
                    record.save()
                    created += 1

                    # 更新汇总表
                    UserQuestionStatus.objects.update_or_create(
                        user=user, question=q,
                        defaults={
                            'attempt_count': 1,
                            'best_score': score,
                            'latest_score': score,
                            'is_correct': score >= 60,
                            'is_in_mistake_book': score < 60,
                            'first_attempt_at': created_at,
                            'last_attempt_at': created_at,
                            'total_time_spent': random.randint(30, 300),
                        }
                    )

        self.stdout.write(f'  新增提交记录: {created} 条')

    def _create_announcements(self):
        self.stdout.write('创建公告...')
        admin = User.objects.filter(role='admin').first()
        announcements = [
            ('系统上线公告', '八股文刷题系统正式上线！欢迎大家注册使用，如有问题请及时反馈。'),
            ('新增推荐算法', '系统已上线基于协同过滤的个性化推荐功能，每日为你推荐最适合的题目。'),
            ('题库更新通知', '本周新增Python后端、计算机网络等多个分类共100+题目，快来刷题吧！'),
        ]
        for title, content in announcements:
            Announcement.objects.get_or_create(
                title=title,
                defaults={'content': content, 'author': admin, 'is_published': True}
            )

    def _compute_similarities(self):
        self.stdout.write('计算相似度矩阵...')
        from apps.recommend.algorithms.user_cf import UserBasedCF
        from apps.recommend.algorithms.item_cf import ItemBasedCF

        user_pairs = UserBasedCF.compute_and_save_all()
        item_pairs = ItemBasedCF.compute_and_save_all()
        self.stdout.write(f'  用户相似度对: {user_pairs}，题目相似度对: {item_pairs}')