import sys
from src.runners.unittest_runner import debug_suit


class LineObject:
    def __init__(self):
        self.count = 0
        self.ctx = []


class Cover:
    def __init__(self, src_name=None, test_name=None):
        self.src_name = src_name
        self.test_name = test_name
        self.counts = {}
        self.current_test = None
        self.globaltrace = self.globaltrace_count
        self.localtrace = self.localtrace_count

    def globaltrace_count(self, frame, why, arg):
        if why == "call":
            filename = frame.f_code.co_filename
            filename = filename.split('\\')[-1]
            if filename == self.src_name:
                return self.localtrace
            if filename != self.test_name:
                return
            func = frame.f_code.co_name
            if func[0] == '<':
                return

            try:
                class_name = frame.f_locals['self'].__class__.__name__
            except (KeyError, AttributeError):
                return

            if filename == self.test_name:
                filename = filename[:-3]
                self.current_test = "%s.%s.%s" % (filename, class_name, func)

        return self.localtrace

    def localtrace_count(self, frame, why, arg):
        if why == "line":
            filename = frame.f_code.co_filename
            filename = filename.split('\\')[-1]
            if filename != self.src_name:
                return

            lineno = frame.f_lineno
            key = lineno
            if self.counts.get(key) is None:
                new_ctx = LineObject()
                new_ctx.count = 1
                new_ctx.ctx.append(self.current_test)
                self.counts[key] = new_ctx
            else:
                old_ctx = self.counts[key]
                old_ctx.count += 1
                if self.current_test not in old_ctx.ctx:
                    old_ctx.ctx.append(self.current_test)

        return self.localtrace

    def run_trace(self):
        sys.settrace(self.globaltrace)
        debug_suit()
        sys.settrace(None)
        return self.counts


if __name__ == '__main__':
    cov = Cover(src_name='dictset.py', test_name='test__dictset.py')
    cov_dict = cov.run_trace()
    for i in cov_dict:
        print(i, cov_dict[i].count, len(cov_dict[i].ctx))

