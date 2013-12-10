def calculate_point(type, data):
    '''
    Type 1: percentage of completion
    Type 2: number of visits
    Type 3: hours since last visit
    '''
    if type == 1:
        if -1 < data < 11:
            return -15
        elif data < 21:
            return -10
        elif data < 31:
            return -5
        elif data < 41:
            return 3
        elif data < 51:
            return 4
        elif data < 61:
            return 5
        elif data < 71:
            return 6
        elif data < 81:
            return 7
        elif data < 91:
            return 10
        else:
            return 15
    elif type == 2:
        if data == 0:
            return 0
        elif data == 1:
            return 1
        elif data == 2:
            return 6
        elif data == 3:
            return 8
        elif data == 4:
            return 8
        elif data == 5:
            return 10
        elif data > 5:
            return 10
    elif type == 3:
        if -1 < data < 11:
            return 0
        elif data < 21:
            return 2
        elif data < 31:
            return 3
        elif data < 41:
            return 4
        elif data < 51:
            return 5
        elif data < 61:
            return 6
        elif data < 71:
            return 7
        elif data < 101:
            return 8
        elif data < 151:
            return 7
        elif data < 201:
            return 6
        elif data < 251:
            return 10
        elif data < 301:
            return 10
        elif data < 401:
            return 7
        elif data < 501:
            return 4
        elif data < 601:
            return -2
        elif data < 701:
            return -10
        else:
            return -25


def get_status_color(points):
    '''
    Return the status color base on total points
    '''
    if points < 5:
        return 'Red'
    elif points < 11:
        return 'Yellow'
    else:
        return 'Green'
