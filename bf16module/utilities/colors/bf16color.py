class BF16color:
    """
    BF16color provides static methods for converting single 8-bit values into various RGB color representations.
    This utility class includes color mapping functions for different color schemes, such as RGB332, grayscale, binary black/white, color scales (red, green, blue), rainbow, CMYK, fire, ice, forest, purple, pastel, neon, thermal, and a special 'circuit' mode.
    Methods:
        rgb332(val): Converts an 8-bit RGB332 value to a 24-bit RGB tuple.
        grayscale(val): Maps a value to a grayscale RGB color.
        binary_bw(val): Maps a value to black or white based on a threshold.
        redscale(val): Maps a value to a red intensity RGB color.
        greenscale(val): Maps a value to a green intensity RGB color.
        bluescale(val): Maps a value to a blue intensity RGB color.
        rainbow(val): Maps a value to a color in the HSV rainbow spectrum.
        cmyk(val): Maps a value to a CMYK-like RGB color.
        fire(val): Maps a value to fire-like (red/orange/yellow) colors.
        ice(val): Maps a value to ice-like (blue/cyan/white) colors.
        forest(val): Maps a value to forest-like (green/brown) colors.
        purple(val): Maps a value to purple-like colors.
        pastel(val): Maps a value to pastel RGB colors.
        neon(val): Maps a value to neon RGB colors.
        thermal(val): Maps a value to thermal-like (blue to red) colors.
        circuit(val): Maps a value to a binary on/off color for circuit-like display.
    """
    @staticmethod
    def rgb332(val):
        """
        Converts an 8-bit RGB332 value to a 24-bit RGB tuple.

        Args:
            val (int): An 8-bit integer representing a color in RGB332 format.

        Returns:
            tuple: A tuple of three integers (r, g, b), each in the range 0-255, representing the color in 24-bit RGB format.

        Example:
            >>> rgb332(0b11100110)
            (255, 36, 204)
        """
        r = ((val >> 5) & 0x07) * 255 // 7
        g = ((val >> 2) & 0x07) * 255 // 7
        b = (val & 0x03) * 255 // 3
        color = (r, g, b)
        return color
    
    @staticmethod
    def grayscale(val):
        """
        Converts a single grayscale value to an RGB color tuple.
        Args:
            val (int): The grayscale intensity value (typically 0-255).
        Returns:
            tuple: An (R, G, B) tuple where each component is set to the input value.
        """
        color = (val, val, val)
        return color

    @staticmethod
    def binary_bw(val):
        """
        Returns a tuple representing a black or white RGB color based on the input value.
        Parameters:
            val (float or int): The value to evaluate, typically in the range [0, 255].
        Returns:
            tuple: (0, 0, 0) for black if val < 127.5, (255, 255, 255) for white if val ≥ 127.5.
        """
        # Black if <127.5, White if ≥128
        return (0, 0, 0) if val < 127.5 else (255, 255, 255)

    @staticmethod
    def redscale(val):
        """
        Converts an integer value to a red color tuple.
        The input value is masked to 8 bits (0-255) and returned as the red component
        of an RGB color, with green and blue components set to 0.
        Args:
            val (int): The input value representing the red intensity.
        Returns:
            tuple: A tuple (R, 0, 0) where R is the masked red value (0-255).
        """
        val &= 0xFF
        return (val, 0, 0)

    @staticmethod
    def greenscale(val):
        """
        Converts an integer value to a green color tuple.
        The input value is masked to 8 bits (0-255) and returned as the green component
        of an RGB color, with red and blue components set to 0.
        Args:
            val (int): The input value representing the green intensity.
        Returns:
            tuple: A tuple (0, G, 0) where G is the masked green value (0-255).
        """
        val &= 0xFF
        return (0, val, 0)

    @staticmethod
    def bluescale(val):
        """
        Converts an integer value to a blue color tuple.
        The input value is masked to 8 bits (0-255) and returned as the blue component
        of an RGB color, with red and green components set to 0.
        Args:
            val (int): The input value representing the blue intensity.
        Returns:
            tuple: A tuple (0, 0, B) where B is the masked blue value (0-255).
        """
        val &= 0xFF
        return (0, 0, val)

    @staticmethod
    def rainbow(val):
        """
        Maps a value to a visible color in a rainbow spectrum using HSV color space.
        Args:
            val (int): The input value (0-255) to map to a color.
        Returns:
            tuple: An (R, G, B) tuple representing the color in the rainbow spectrum.
        """
        import colorsys
        h = (val % 256) / 256.0
        r, g, b = colorsys.hsv_to_rgb(h, 1.0, 1.0)
        return (int(r * 255), int(g * 255), int(b * 255))

    @staticmethod
    def cmyk(val):
        """
        Maps a value to CMYK-like colors, then converts to RGB for display.
        Args:
            val (int): The input value (0-255) to map to a CMYK color.
        Returns:
            tuple: An (R, G, B) tuple representing the CMYK-mapped color.
        """
        c = ((val >> 6) & 0x03) * 255 // 3  # Cyan
        m = ((val >> 4) & 0x03) * 255 // 3  # Magenta
        y = ((val >> 2) & 0x03) * 255 // 3  # Yellow
        k = (val & 0x03) * 255 // 3         # Black (inverted for display)

        # Convert CMYK to RGB for display
        r = 255 - min(255, c + k)
        g = 255 - min(255, m + k)
        b = 255 - min(255, y + k)
        return (r, g, b)

    @staticmethod
    def fire(val):
        """
        Maps a value to fire-like colors (red, orange, yellow).
        Args:
            val (int): The input value (0-255) to map to a fire color.
        Returns:
            tuple: An (R, G, B) tuple representing a fire-like color.
        """
        r = min(255, val * 2)
        g = min(255, (val - 64) * 2) if val > 64 else 0
        b = min(255, (val - 128) * 2) if val > 128 else 0
        return (r, g, b)

    @staticmethod
    def ice(val):
        """
        Maps a value to ice-like colors (blue, cyan, white).
        Args:
            val (int): The input value (0-255) to map to an ice color.
        Returns:
            tuple: An (R, G, B) tuple representing an ice-like color.
        """
        r = min(255, (val - 128) * 2) if val > 128 else 0
        g = min(255, (val - 64) * 2) if val > 64 else 0
        b = min(255, val * 2)
        return (r, g, b)

    @staticmethod
    def forest(val):
        """
        Maps a value to forest-like colors (greens, browns).
        Args:
            val (int): The input value (0-255) to map to a forest color.
        Returns:
            tuple: An (R, G, B) tuple representing a forest-like color.
        """
        r = min(255, val // 2 + 50)
        g = min(255, val * 2)
        b = min(255, val // 4)
        return (r, g, b)

    @staticmethod
    def purple(val):
        """
        Maps a value to purple-like colors.
        Args:
            val (int): The input value (0-255) to map to a purple color.
        Returns:
            tuple: An (R, G, B) tuple representing a purple-like color.
        """
        r = min(255, val * 1)
        g = 0
        b = min(255, val * 1.5)
        return (r, g, b)
    
    @staticmethod
    def pastel(val):
        """
        Maps a value to pastel colors (soft, light tones).
        Args:
            val (int): The input value (0-255) to map to a pastel color.
        Returns:
            tuple: An (R, G, B) tuple representing a pastel color.
        """
        r = 128 + (val // 2)
        g = 128 + (val // 3)
        b = 128 + (val // 4)
        return (min(255, r), min(255, g), min(255, b))
    
    @staticmethod
    def neon(val):
        """
        Maps a value to neon colors (bright, saturated colors).
        Args:
            val (int): The input value (0-255) to map to a neon color.
        Returns:
            tuple: An (R, G, B) tuple representing a neon color.
        """
        r = 0
        g = 0
        b = 0
        if val < 85: # Neon Green
            r = int(val * 3)
            g = 255
        elif val < 170: # Neon Blue
            g = 255 - int((val - 85) * 3)
            b = 255
        else: # Neon Pink
            r = 255
            b = 255 - int((val - 170) * 3)
        return (r, g, b)
    
    @staticmethod
    def thermal(val):
        """
        Maps a value to thermal-like colors (blue to red gradient).
        Blue at low values, transitioning to red at high values.
        Args:
            val (int): The input value (0-255) to map to a thermal color.
        Returns:
            tuple: An (R, G, B) tuple representing a thermal color.
        """
        r = min(255, val * 2)
        g = min(255, val * 2) if val < 128 else max(0, 255 - (val - 128) * 2)
        b = max(0, 255 - val * 2)
        return (r, g, b)
    
    @staticmethod
    def circuit(val):
        """ TBS (the broken script) Circuit Texture LOL
        Args:
            val (int): The input value (0-255) to map to a circuit spaghetti? wire?.
        Returns:
            tuple: (255, 255, 255) if val >= 3, else (0, 0, 0).
        """
        val = 255 if val >= 3 else 0
        return (val, val, val)