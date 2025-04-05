import cv2
import numpy as np

def apply_filters(image_path, filters, output_path):
    img = cv2.imread(image_path)

    for f in filters:
        name = f.get("name")
        params = f.get("params", {})

        if name == "gray":
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        elif name == "blur":
            k = int(params.get("ksize", 5))
            img = cv2.GaussianBlur(img, (k, k), 0)

        elif name == "threshold":
            thresh = int(params.get("thresh", 127))
            maxval = int(params.get("maxval", 255))
            _, img = cv2.threshold(img, thresh, maxval, cv2.THRESH_BINARY)

        elif name == "erode":
            k = int(params.get("kernel", 3))
            iterations = int(params.get("iterations", 1))
            kernel = np.ones((k, k), np.uint8)
            img = cv2.erode(img, kernel, iterations=iterations)

        elif name == "dilate":
            k = int(params.get("kernel", 3))
            iterations = int(params.get("iterations", 1))
            kernel = np.ones((k, k), np.uint8)
            img = cv2.dilate(img, kernel, iterations=iterations)

        elif name == "open":
            k = int(params.get("kernel", 3))
            kernel = np.ones((k, k), np.uint8)
            img = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)

        elif name == "close":
            k = int(params.get("kernel", 3))
            kernel = np.ones((k, k), np.uint8)
            img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)

        elif name == "canny":
            t1 = int(params.get("threshold1", 100))
            t2 = int(params.get("threshold2", 200))
            img = cv2.Canny(img, t1, t2)

        elif name == "invert":
            img = cv2.bitwise_not(img)

    # Salva a imagem final
    cv2.imwrite(output_path, img)


def generate_code(filters):
    lines = [
        "import cv2",
        "import numpy as np",
        "",
        "img = cv2.imread('sua_imagem.png')"
    ]

    for f in filters:
        name = f.get("name")
        params = f.get("params", {})

        if name == "gray":
            lines.append("img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)")

        elif name == "blur":
            k = int(params.get("ksize", 5))
            lines.append(f"img = cv2.GaussianBlur(img, ({k}, {k}), 0)")

        elif name == "threshold":
            thresh = int(params.get("thresh", 127))
            maxval = int(params.get("maxval", 255))
            lines.append(f"_, img = cv2.threshold(img, {thresh}, {maxval}, cv2.THRESH_BINARY)")

        elif name == "erode":
            k = int(params.get("kernel", 3))
            iterations = int(params.get("iterations", 1))
            lines.append(f"kernel = np.ones(({k}, {k}), np.uint8)")
            lines.append(f"img = cv2.erode(img, kernel, iterations={iterations})")

        elif name == "dilate":
            k = int(params.get("kernel", 3))
            iterations = int(params.get("iterations", 1))
            lines.append(f"kernel = np.ones(({k}, {k}), np.uint8)")
            lines.append(f"img = cv2.dilate(img, kernel, iterations={iterations})")

        elif name == "open":
            k = int(params.get("kernel", 3))
            lines.append(f"kernel = np.ones(({k}, {k}), np.uint8)")
            lines.append("img = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)")

        elif name == "close":
            k = int(params.get("kernel", 3))
            lines.append(f"kernel = np.ones(({k}, {k}), np.uint8)")
            lines.append("img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)")

        elif name == "canny":
            t1 = int(params.get("threshold1", 100))
            t2 = int(params.get("threshold2", 200))
            lines.append(f"img = cv2.Canny(img, {t1}, {t2})")

        elif name == "invert":
            lines.append("img = cv2.bitwise_not(img)")

    lines.append("cv2.imwrite('output.png', img)")

    return '\n'.join(lines)
