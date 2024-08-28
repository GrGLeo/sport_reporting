from fitparse import FitFile

fitfile = FitFile('run.fit')

for record in fitfile.get_messages('record'):
    for data in record:
        print(f'{data.name}: {data.value}')
