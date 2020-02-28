import sys

from src.runners.unittest_runner import debug_suit


class LineObject:
    def __init__(self):
        self.count = 0
        self.ctx = []


class Cover:
    def __init__(self, prg_name=None, src_name=None, test_name=None):
        self.prg_name = prg_name
        self.src_name = src_name
        self.test_name = test_name
        self.src_counts = {}

        for file in src_name:
            self.src_counts[file] = {}

        self.current_test = None
        self.globaltrace = self.globaltrace_count
        self.localtrace = self.localtrace_count

    def globaltrace_count(self, frame, why, arg):
        if why == "call":
            filename = frame.f_code.co_filename
            filename = filename.split('\\')[-1]
            if filename in self.src_name:
                return self.localtrace
            if filename not in self.test_name:
                return
            func = frame.f_code.co_name
            if func[0] == '<':
                return

            try:
                class_name = frame.f_locals['self'].__class__.__name__
            except (KeyError, AttributeError):
                return

            if filename in self.test_name:
                filename = filename[:-3]
                self.current_test = "%s.%s.%s" % (filename, class_name, func)

        return self.localtrace

    def localtrace_count(self, frame, why, arg):
        if why == "line":
            filename = frame.f_code.co_filename
            filename = filename.split('\\')[-1]
            if filename not in self.src_name:
                return
            current_dict = self.src_counts[filename]
            lineno = frame.f_lineno
            key = lineno
            if current_dict.get(key) is None:
                new_ctx = LineObject()
                new_ctx.count = 1
                new_ctx.ctx.append(self.current_test)
                current_dict[key] = new_ctx
            else:
                old_ctx = current_dict[key]
                old_ctx.count += 1
                if self.current_test not in old_ctx.ctx:
                    old_ctx.ctx.append(self.current_test)

        return self.localtrace

    def run_trace(self):
        sys.settrace(self.globaltrace)
        debug_suit(self.prg_name)
        sys.settrace(None)
        return self.src_counts


if __name__ == '__main__':

    cov = Cover(prg_name='astmonkey', src_name=['transformers.py'],
                test_name=['test_transformers.py'])
    cov_dict = cov.run_trace()
    for key in cov_dict['transformers.py'].keys():
        print(key, cov_dict['transformers.py'][key].ctx)

    

