def get_data(fitfile, field):
    field_data = []
    for line in fitfile.get_messages(field):
        line_data = {}
        for data in line:
            line_data[data.name] = data.value
        field_data.append(line_data)
    return field_data
