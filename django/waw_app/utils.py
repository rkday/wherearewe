class ColourCoordinator:
    def __init__(self, min, max, num_steps, start_colour, end_colour):
        self.groups = {}
        step_iter = count(min, (max - min) / float(num_steps))
        red_colours = self.colour_strings_to_steps(start_colour[1:3],
                                                   end_colour[1:3],
                                                   num_steps)
        green_colours = self.colour_strings_to_steps(start_colour[3:5],
                                                     end_colour[3:5],
                                                     num_steps)
        blue_colours = self.colour_strings_to_steps(start_colour[5:7],
                                                    end_colour[5:7],
                                                    num_steps)

        step = step_iter.next()
        while True:
            print step
            step = int(step_iter.next())
            colour = "#%02x%02x%02x" % (red_colours.next(),
                                        green_colours.next(),
                                        blue_colours.next())
            if step not in self.groups:
                self.groups[step] = colour
            if step >= max:
                self.groups[step] = end_colour
                break

    def colour_strings_to_steps(self, from_str, to_str, num_steps):

        """Converts two strings representing colours, such as "ff" and "c0", to
        a sequence of numbers representing the steps between them (e.g. 256,
        250...192)"""

        start = int(from_str, 16)
        end = int(to_str, 16)
        distance = end - start
        step_length = distance / float(num_steps)
        return count(start, step_length)

    def get_colour_mapping(self, count):
	if not count:
            return "#ffffff"
        for key in sorted(self.groups.keys()):
            if count <= key:
                return self.groups[key]

def count(start=0, step=1):
    # count(10) --> 10 11 12 13 14 ...
    # count(2.5, 0.5) -> 2.5 3.0 3.5 ...
    n = start
    while True:
        yield n
        n += step

if __name__ == "__main__":
	print ColourCoordinator(1, 2, 30, "#ffffff", "#0000ff").get_colour_mapping(2)
