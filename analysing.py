import re

def parse_salary_strict(text: str):
    min_salary = None
    max_salary = None

    nums = re.findall(r"\d[\d\s]*", text)
    nums = [int(n.replace(" ", "")) for n in nums]

    if  re.search(r"[–—-]", text) and len(nums) >= 2:
        min_salary = nums[0]
        max_salary = nums[1]
    elif "до" in text and len(nums) == 1:
        max_salary = nums[0]
    elif "от" in text and len(nums) == 1:
        min_salary = nums[0]

    return [min_salary, max_salary]

def analyse(data):
    if len(data) == 0:
        data.append(1)
    salarys_not_null = []
    exp_with_not_null = []
    salary_analyse = []
    expirience_analyse = {
        '0' : [],
        '1-3' : [],
        '3-6' : [],
        '6' : []
    }

    for i in data:
        if i[1] != 'Not Available':
            salarys_not_null.append(i[1])
            exp_with_not_null.append(i[2])


    for index, salary in enumerate(salarys_not_null): # cleaning salary value
        salary_analyse.append(parse_salary_strict(salary))
        if exp_with_not_null[index] == 'Без опыта':
            expirience_analyse['0'].append(parse_salary_strict(salary))
        elif exp_with_not_null[index] == 'Опыт 1-3 года':
            expirience_analyse['1-3'].append(parse_salary_strict(salary))
        elif exp_with_not_null[index] == 'Опыт 3-6 лет':
            expirience_analyse['3-6'].append(parse_salary_strict(salary))
        elif exp_with_not_null[index] == 'Опыт более 6 лет':
            expirience_analyse['6'].append(parse_salary_strict(salary))


    # summing minimum and max values
    min_mean_l = []
    min_mean = 0
    max_mean_l = []
    max_mean = 0
    for i in salary_analyse:
        if i[0] is not None:
            min_mean_l.append(i[0])
            min_mean += i[0]
        if i[1] is not None:
            max_mean_l.append(i[1])
            max_mean += i[1]

    min_mean = round(sum(min_mean_l) / len(min_mean_l) if min_mean_l else 0)
    max_mean = round(sum(max_mean_l) / len(max_mean_l) if max_mean_l else 0)
    mean = round((min_mean + max_mean) / 2)
    disclosed_salary = str(round((len(salarys_not_null) / len(data)) * 100, 2)) + '%'

    for category in list(expirience_analyse.keys()):
        amount = 0
        lenght = 0
        for value in expirience_analyse[category]:
            if value[0] and value[1]:
                amount += value[0] + value[1]
                lenght += 2
            elif value[0]:
                amount += value[0]
                lenght+= 1
            elif value[1]:
                amount += value[1]
                lenght += 1

            expirience_analyse[category] = round(amount/lenght)

    salary_analyse = {'max mean salary' : max_mean, 'min mean salary' : min_mean, 'mean salary' : mean, 'disclosed salary' : disclosed_salary}
    expirience_analyse['Without experience'] = expirience_analyse.pop('0')
    expirience_analyse['Experience 1-3 years'] = expirience_analyse.pop('1-3')
    expirience_analyse['Experience 3-6 years'] = expirience_analyse.pop('3-6')
    expirience_analyse['Experienve more 6 years'] = expirience_analyse.pop('6')

    return [salary_analyse,expirience_analyse]