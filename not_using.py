def generate_source_files():
    exclude = {'runners', 'tests', '__pycache__'}
    src_include_list = []
    for root, dirs, files in os.walk(top='src', topdown=True):
        dirs[:] = [d for d in dirs if d not in exclude]
        for file_s in files:
            src_include_list.append(file_s)
    return src_include_list



def create_assert_dict(cov_data):
    assert_dict = {}
    unique_filenames = []
    for x in cov_data.measured_contexts():  # x = module.class.test_case
        unique_filenames.append(x.split('.')[0])

    unique_filenames = set(unique_filenames)

    for x in unique_filenames:
        assert_dict.update(AssertCounter(x).assert_dict)
    return assert_dict, unique_filenames


def create_feature_dict(py_files, assert_dict, cov_results):
    src_ftr_dict = {}
    for py_file in py_files:
        ftr_dict = {}
        # per src create ftr_dict
        line_no = 1
        if os.path.exists('cover/src.' + py_file[:-3] + '.cover'):
            with open('cover/src.' + py_file[:-3] + '.cover') as f:
                for line in f:
                    match_obj = re.match(' {4}(\\d+)', line)
                    if match_obj:
                        ftr_dict[line_no] = [int(match_obj.group(1))]
                    line_no += 1
        ctx_assert_dict = merge_ctx_and_assert_dict(py_file, cov_results, assert_dict)
        for x in ctx_assert_dict:
            ftr_dict[x] = ftr_dict[x] + ctx_assert_dict[x]
        for y in ftr_dict:
            if len(ftr_dict[y]) == 1:
                ftr_dict[y] = ftr_dict[y] + [0, 0, 0]
        src_ftr_dict[py_file] = ftr_dict
    return src_ftr_dict

def merge_ctx_and_assert_dict(ctx_file, ctx_results, assert_dict):
    # TODO what if a line is hit by more than one class
    ctx_hold_dict = dict(ctx_results.contexts_by_lineno(os.getcwd() + '\src\\' + ctx_file))
    ctx_assert_dict = {}

    for ctx_lineno, ctx_methods in ctx_hold_dict.items():
        ctx_assert_dict[ctx_lineno] = [len(ctx_methods), 0, 0]
        for ctx_method in ctx_methods:
            ctx_assert_dict[ctx_lineno][1] = assert_dict[ctx_method][0]
            ctx_assert_dict[ctx_lineno][2] += assert_dict[ctx_method][1]
    return ctx_assert_dict


# (src_list, dyn_ftr_dict, src_mut_dict)
def update_dyn_ftr(file_list, dyn_dict, mut_dict):
    for file_src in file_list:
        ftr_dict = dyn_dict[file_src]
        mutant_list = mut_dict[file_src]
        org_mut_dict = mutant_list.mutations
        for lineno in org_mut_dict:
            for mut_obj in org_mut_dict[lineno]:
                if lineno in ftr_dict.keys():
                    mut_obj.update_ftr(ftr_dict[lineno])






# Original Base Generate Mutants


    def generate_mutants(self, mutation_list=None, mutation_number=None):
        self.mutation_list = mutation_list
        self.filename = src_file
        self.mutant_number = mutation_number

        directory, module_name = os.path.split(src_file)
        module_name = os.path.splitext(module_name)[0]

        path = list(sys.path)
        sys.path.insert(0, directory)
        try:
            self.module = __import__(module_name)
        finally:
            sys.path[:] = path  # restore

        with open(src_file) as f:
            module = ast.parse(f.read())
            self.visit(module)
            return self.mutation_list, self.mutant_number