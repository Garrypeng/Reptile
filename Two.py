class B:
    def __init__(self, un='', pw=''):
        self.un = un
        self.pw = pw

    def get_parameter(self):
        # if '123' is self.un:
        #     return True
        # else:
        #     return False
        return self.un, self.pw


class RPT:
    def __init__(self, kw):
        self.search_terms = kw['search_terms']
        self.famous_enterprise = kw['famous_enterprise']
        self.target_city_section = kw['target_city_section']
        self.expected_salary = kw['expected_salary']
        self.release_time = kw['release_time']
        self.work_experience = kw['work_experience']
        self.education = kw['education']
        self.expected_industry = kw['expected_industry']
        self.expected_position = kw['expected_position']
        self.enterprise_scale = kw['enterprise_scale']
        self.financing_stage = kw['financing_stage']
        self.enterprise_nature = kw['enterprise_nature']

    def get_parameter(self):
        return self.search_terms, self.famous_enterprise, self.target_city_section, self.expected_salary, self.release_time, \
               self.work_experience, self.education, self.expected_industry, self.expected_position, self.enterprise_scale, \
               self.financing_stage, self.enterprise_nature
