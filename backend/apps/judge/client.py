import subprocess
import tempfile
import os
import time
import shutil


LANGUAGE_CONFIG = {
    'python': {
        'ext': '.py',
        'compile': None,
        'run': ['python', '{file}'],
    },
    'javascript': {
        'ext': '.js',
        'compile': None,
        'run': ['node', '{file}'],
    },
    'java': {
        'ext': '.java',
        'compile': ['javac', '{file}'],
        'run': ['java', '-cp', '{dir}', 'Main'],
    },
    'cpp': {
        'ext': '.cpp',
        'compile': ['g++', '-o', '{dir}/a.exe', '{file}'],
        'run': ['{dir}/a.exe'],
    },
    'c': {
        'ext': '.c',
        'compile': ['gcc', '-o', '{dir}/a.exe', '{file}'],
        'run': ['{dir}/a.exe'],
    },
    'go': {
        'ext': '.go',
        'compile': None,
        'run': ['go', 'run', '{file}'],
    },
}


class Judge0Client:
    """本地判题客户端（subprocess实现）"""

    def submit_and_wait(self, source_code, language, stdin='',
                        expected_output='', time_limit=None, memory_limit=None,
                        max_wait=30):
        config = LANGUAGE_CONFIG.get(language)
        if not config:
            return {
                'status_id': 14,
                'status_desc': 'Unsupported language: ' + language,
                'stdout': '', 'stderr': '', 'compile_output': '',
                'time': 0, 'memory': 0,
            }

        timeout = (time_limit / 1000) if time_limit else 10
        tmpdir = tempfile.mkdtemp(prefix='judge_')

        try:
            if language == 'java':
                filename = 'Main' + config['ext']
            else:
                filename = 'solution' + config['ext']

            filepath = os.path.join(tmpdir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(source_code)

            # 编译阶段
            if config['compile']:
                compile_cmd = [
                    c.replace('{file}', filepath).replace('{dir}', tmpdir)
                    for c in config['compile']
                ]
                try:
                    cr = subprocess.run(
                        compile_cmd, capture_output=True, text=True,
                        timeout=30, cwd=tmpdir,
                    )
                    if cr.returncode != 0:
                        return {
                            'status_id': 6, 'status_desc': 'Compilation Error',
                            'stdout': '', 'stderr': '',
                            'compile_output': cr.stderr[:1000],
                            'time': 0, 'memory': 0,
                        }
                except FileNotFoundError:
                    return {
                        'status_id': 6, 'status_desc': 'Compilation Error',
                        'stdout': '', 'stderr': '',
                        'compile_output': '环境配置错误：未找到编译命令。请联系管理员安装相关语言环境。',
                        'time': 0, 'memory': 0,
                    }
                except subprocess.TimeoutExpired:
                    return {
                        'status_id': 6, 'status_desc': 'Compilation Error',
                        'stdout': '', 'stderr': '',
                        'compile_output': 'Compilation timeout',
                        'time': 0, 'memory': 0,
                    }

            # 运行阶段
            run_cmd = [
                c.replace('{file}', filepath).replace('{dir}', tmpdir)
                for c in config['run']
            ]

            start_time = time.time()
            try:
                rr = subprocess.run(
                    run_cmd, input=stdin,
                    capture_output=True, text=True,
                    timeout=timeout, cwd=tmpdir,
                )
                elapsed = round((time.time() - start_time) * 1000, 2)
                stdout = rr.stdout.strip()
                stderr = rr.stderr.strip()

                if rr.returncode != 0:
                    return {
                        'status_id': 11, 'status_desc': 'Runtime Error (NZEC)',
                        'stdout': stdout, 'stderr': stderr[:1000],
                        'compile_output': '',
                        'time': elapsed / 1000, 'memory': 0,
                    }

                expected = expected_output.strip()
                if stdout == expected:
                    status_id = 3
                    status_desc = 'Accepted'
                else:
                    status_id = 4
                    status_desc = 'Wrong Answer'

                return {
                    'status_id': status_id, 'status_desc': status_desc,
                    'stdout': stdout, 'stderr': stderr[:500],
                    'compile_output': '',
                    'time': elapsed / 1000, 'memory': 0,
                }

            except FileNotFoundError:
                return {
                    'status_id': 13, 'status_desc': 'System Error',
                    'stdout': '', 'stderr': '',
                    'compile_output': '环境配置错误：未找到运行命令。请联系管理员安装相关语言环境。',
                    'time': 0, 'memory': 0,
                }

            except subprocess.TimeoutExpired:
                elapsed = round((time.time() - start_time) * 1000, 2)
                return {
                    'status_id': 5, 'status_desc': 'Time Limit Exceeded',
                    'stdout': '', 'stderr': '', 'compile_output': '',
                    'time': elapsed / 1000, 'memory': 0,
                }

        finally:
            try:
                shutil.rmtree(tmpdir, ignore_errors=True)
            except Exception:
                pass

    @staticmethod
    def map_status(status_id):
        from apps.judge.models import JudgeTask
        mapping = {
            3: JudgeTask.Status.ACCEPTED,
            4: JudgeTask.Status.WRONG_ANSWER,
            5: JudgeTask.Status.TIME_LIMIT,
            6: JudgeTask.Status.COMPILE_ERROR,
            11: JudgeTask.Status.RUNTIME_ERROR,
            13: JudgeTask.Status.SYSTEM_ERROR,
            14: JudgeTask.Status.SYSTEM_ERROR,
        }
        return mapping.get(status_id, JudgeTask.Status.SYSTEM_ERROR)