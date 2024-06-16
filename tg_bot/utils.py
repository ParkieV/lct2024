def isFloat(element: any) -> bool:
    if element is None:
        return False
    try:
        float(element)
        return True
    except ValueError:
        return False
