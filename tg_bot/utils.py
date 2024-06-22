import base64


def isFloat(element: any) -> bool:
    if element is None:
        return False
    try:
        float(element)
        return True
    except ValueError:
        return False


def base64ToBufferInputStream(img_base_64: str) -> bytes:
    imgBytes = img_base_64.encode(encoding='UTF-8')
    print(img_base_64)
    print()
    print()
    return base64.decodebytes(imgBytes)
