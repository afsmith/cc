"""
    Formats progress value to
    a UI-friendly format: 0, 10, 20 ... 100%.
    This type of formatting is needed by several
    views to display an appropriate icon
    visualizing progress.
"""
def progress_formatter(progress):
    if progress == 0:
        return 0
    elif progress < 0.15:
        return 10
    elif progress > 0.85 and progress < 1:
        return 90
 
    return int(round(progress * 10) * 10)