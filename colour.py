class MetaColour:
    MIN_VALUE_IDX = 0
    MAX_VALUE_IDX = 1
    metadata = None
    order = None

    def __init__(self, values: dict):
        self.values = values
        print(values, self.metadata)
        for key in self.metadata:
            value = values[key]
            max_value = self.max_value(key)
            min_value = self.min_value(key)
            if value > max_value or value < min_value:
                raise ValueError("{param_name} = {param_value} higher than {max_value} or less than {min_value}".format(
                                 param_name=key, param_value=value, max_value=max_value, min_value=min_value))

    def min_value(self, key):
        return self.metadata[key][self.MIN_VALUE_IDX]

    def max_value(self, key):
        return self.metadata[key][self.MAX_VALUE_IDX]

    def str(self):
        result = ""
        for key in self.order:
            result = result + "{param_name}={param_value} ".format(param_name=key, param_value=self.values[key])
        return result

    def get(self, key):
        return self.values[key]

    def get_all(self):
        result = []
        for key in self.order:
            result.append(self.get(key))
        return result

    def set(self, key, value):
        self.values[key] = value


class RGB(MetaColour):
    r = "r"
    g = "g"
    b = "b"
    order = [r, g, b]
    metadata = {
        r: (0, 255),
        g: (0, 255),
        b: (0, 255)
    }

    def __init__(self, rv=0, gv=0, bv=0):
        super(RGB, self).__init__({self.r: rv, self.g: gv, self.b: bv})


class CMYK(MetaColour):
    c = "c"
    m = "m"
    y = "y"
    k = "k"
    order = [c, m, y, k]
    metadata = {
        c: (0, 100),
        m: (0, 100),
        y: (0, 100),
        k: (0, 100)
    }

    def __init__(self, cv, mv, yv, kv):
        super(CMYK, self).__init__({self.c: cv, self.m: mv, self.y: yv, self.k: kv})


class HSV(MetaColour):
    h = "h"
    s = "s"
    v = "v"
    order = [h, s, v]
    metadata = {
        h: (0, 360),
        s: (0, 100),
        v: (0, 100)
    }

    def __init__(self, hv, sv, vv):
        super(HSV, self).__init__({self.h: hv, self.s: sv, self.v: vv})


class ColourTranslator:
    @staticmethod
    def rgb_to_cmyk(rgb: RGB) -> CMYK:
        def get_k_condident(value):
            return 100 - value/2.55
        k = min(get_k_condident(rgb.get(RGB.r)), get_k_condident(rgb.get(RGB.g)), get_k_condident(rgb.get(rgb.b)))

        def get_cmy_component(value):
            return 255*(1-value)*(1-k)
        c = get_cmy_component(rgb.r)
        m = get_cmy_component(rgb.g)
        y = get_cmy_component(rgb.b)
        return CMYK(c, m, y, k)

    @staticmethod
    def cmyk_to_rgb(cmyk: CMYK) -> RGB:
        c, m, y, k = cmyk.get_all()

        def get_rgb_component(value):
            return 255*(1-value/100)*(1-k/100)
        r = get_rgb_component(c)
        g = get_rgb_component(m)
        b = get_rgb_component(y)
        return RGB(r, g, b)

    @staticmethod
    def hsv_to_rgb(hsv: HSV) -> RGB:
        h, s, v = hsv.get_all()

        c = v * s
        x = c * (1 - abs((h/60) % 2 - 1))
        m = v - c

        if h < 60 or h == 360:
            r0, g0, b0 = c, x, 0
        elif h < 120:
            r0, g0, b0 = x, c, 0
        elif h < 180:
            r0, g0, b0 = 0, c, x
        elif h < 240:
            r0, g0, b0 = 0, x, c
        elif h < 300:
            r0, g0, b0 = x, 0, c
        elif h < 360:
            r0, g0, b0 = c, 0, x
        else:
            raise ValueError(hsv)

        def get_rgb_component(value):
            return (value + m) * 255
        r, g, b = get_rgb_component(r0), get_rgb_component(g0), get_rgb_component(b0)

        return RGB(r, g, b)

    @staticmethod
    def rgb_to_hsv(rgb: RGB) -> HSV:
        r, g, b = rgb.get_all()

        r0 = r/255
        g0 = g/255
        b0 = b/255

        cmax = max(r0, g0, b0)
        cmin = min(r0, g0, b0)

        delta = cmax - cmin

        if delta == 0:
            h = 0
        elif cmax == r0:
            h = 60 * (((g0 - b0) / delta) % 6)
        elif cmax == g0:
            h = 60 * ((b0 - r0) / delta + 2)
        else:
            h = 60 * ((r0 - g0) / delta + 4)

        if cmax == 0:
            s = 0
        else:
            s = delta / cmax

        v = cmax

        return HSV(h, s, v)

    @staticmethod
    def hsv_to_cmyk(hsv: HSV) -> CMYK:
        return ColourTranslator.rgb_to_cmyk(ColourTranslator.hsv_to_rgb(hsv))

    @staticmethod
    def cmyk_to_hsv(cmyk: CMYK) -> HSV:
        return ColourTranslator.rgb_to_hsv(ColourTranslator.cmyk_to_rgb(cmyk))
