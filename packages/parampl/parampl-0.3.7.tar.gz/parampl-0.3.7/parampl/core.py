import matplotlib.artist
import numpy as np
from matplotlib.axes import Axes

from parampl.statics import (split_into_paragraphs, parse_avoid,
                             avoid_specification, avoid_single_specification, get_aspect)

rectangle_specification = tuple[float, float, float, float]  # left, right, bottom, top

__all__ = ['ParaMPL', 'avoid_specification', 'avoid_single_specification']


class _line_position:
    def __repr__(self):
        return f"Line's position currently at {self.x}, {self.y}: borders: {self.borders}"

    def __init__(self,
                 xy,
                 width, height,
                 rotation, spacing,
                 ha, justify,
                 y_to_x_ratio=1.0,
                 xy_at_top=True):
        self.x_orig, self.y_orig = xy
        self.width = width
        self.height = height
        self.rotation = rotation

        if ha == 'right':
            self.x_orig -= width
        elif ha == 'center':
            self.x_orig -= width / 2.0
        elif ha != 'left':
            raise ValueError(f"invalid ha '{ha}'. Must be 'right', 'left', or 'center'")

        if xy_at_top:
            self.y_orig -= height * np.cos(rotation * np.pi / 180)  # top alignment
            self.x_orig -= height * np.sin(rotation * np.pi / 180)  # top alignment

        self.delta_x = spacing * height * np.sin(rotation * np.pi / 180) * y_to_x_ratio
        self.delta_y = - spacing * height * np.cos(rotation * np.pi / 180)

        self.borders = [(None, self.x_orig, width)]
        self.limit: float | None = None
        self.x = self.x_orig
        self.width_line = self.width

        self.y = self.y_orig

        self.justify_mult = (justify == 'right') + 0.5 * (justify == 'center')
        if justify not in ['right', 'center', 'left', 'full']:
            raise ValueError(f'Unrecognized justify {justify}')

    def check_next_border(self, force=False):
        if force:
            self.limit, self.x, self.width_line = self.borders.pop(0)
        while self.limit is not None and self.y < self.limit:
            self.limit, self.x, self.width_line = self.borders.pop(0)

    def add_rectangles(self, rectangles):
        x = self.x_orig
        w = self.width

        avoid_left = []
        avoid_right = []
        for left, right, bottom, top in rectangles:
            left_space = left - x
            right_space = x + w - right
            if left_space <= 0 and right_space <= 0:
                print(f"Rectangle with limits ({left:.2g}, {right:.2g}, {bottom:2g}, {top:.2g}) leaves no writable "
                      f"space when starting at x: {x} and width: {w}. \n Since it is not yet supported to skip "
                      f"a horizontally-spanning slab, this rectangle is ignored.")
                continue
            if left_space < right_space:
                avoid_left.append((right, (bottom, top)))
            else:
                avoid_right.append((left, (bottom, top)))

        self.add_avoids(avoid_left, avoid_right)

    def add_avoids(self, avoid_left_of, avoid_right_of, initialize=False):
        if avoid_left_of is not None or avoid_right_of is not None:
            self.borders = parse_avoid(self.borders, avoid_left_of, avoid_right_of, self.height)

        self.check_next_border(force=initialize)
        pass

    def offset(self,
               offset: float = 0,
               justified_length: float = 0,
               ) -> tuple[float, float]:
        total_offset = self.justify_mult * (self.width_line - justified_length) + offset
        return (self.x + total_offset * np.cos(self.rotation * np.pi / 180),
                self.y + total_offset * np.sin(self.rotation * np.pi / 180))

    def next_line(self):
        self.x += self.delta_x
        self.y += self.delta_y

        self.check_next_border()

    def total_height(self):
        return ((self.y_orig - self.y) * np.cos(self.rotation * np.pi / 180) +
                self.width * np.sin(self.rotation*np.pi / 180))

    def y_to_bottom_offset(self):
        lowest = min(self.y,
                     self.y + self.width * np.sin(self.rotation*np.pi/180),
                     self.y_orig + self.delta_y,
                     self.y_orig + self.delta_y + self.width * np.sin(self.rotation*np.pi/180),
                     )
        return self.y_orig - lowest


class ParaMPL:
    """
    ParaMPL object is able to write justified text for a particular axes.  Default values can be fixed at
    initialization, but each time the write() method is used the text properties can be changed individually.

    Parameters
    ----------
    axes
      matplotlib.axes.Axes in which to put the paragraphs
    transform
      the transform in which the coordinates are given. Currently supported: 'data'
    width
       default width
    spacing
      default spacing
    fontname
       default font name
    fontsize
       default fontsize, uses matplotlib's value at initialization if not specified
    family
       default font family, uses matplotlib's value at initialization if not specified
    weight
       default font weight, uses matplotlib's value at initialization if not specified
    style
       default style, uses matplotlib's value at initialization if not specified
    color
      default text color
    rotation
      default text rotation
    justify
      default text justification
    zorder
      default zorder
    """

    def __init__(self,
                 axes: Axes,
                 transform: str = 'data',

                 width: float = 1.0,
                 spacing: float = 1.3,

                 fontname: str | None = None,
                 fontsize: float = None,
                 family: str | None = None,
                 weight: str | None = None,
                 style: str | None = None,

                 color: None | str | tuple[float, float, float] = None,
                 rotation: float = 0.0,
                 justify: str = "left",
                 zorder: float | None = 3,
                 ):

        if family is None:
            family = matplotlib.rcParams['font.family'][0]
        if fontsize is None:
            fontsize = matplotlib.rcParams['font.size']
        if weight is None:
            weight = matplotlib.rcParams['font.weight']
        if style is None:
            style = matplotlib.rcParams['font.style']

        self._text_props = {'fontname': fontname,

                            'fontsize': fontsize,
                            'family': family,
                            'weight': weight,
                            'style': style,

                            'color': color,
                            'rotation': rotation,
                            'zorder': zorder,
                            }

        self._width = width
        self._spacing = spacing
        self._justify = justify

        self.leftover: str = ""

        self._axes = axes

        self._renderer = axes.get_figure().canvas.get_renderer()
        if transform == 'data':
            self._transform = axes.transData.inverted()
        else:
            raise NotImplementedError("only 'data' transform is supported for now")

        self._widths: dict[tuple, dict[str, float]] = {}
        self._heights: dict[tuple, float] = {}
        self._rectangles: list[rectangle_specification] = []

    def get_axes(self):
        """Return matplotlib axes being used"""
        return self._axes

    def avoid_rectangle(self,
                        left: float,
                        bottom: float,
                        width: float,
                        height: float,
                        ):
        """
        add rectangles to avoid based on its dimensions

        Parameters
        ----------
        left
          horizontal left limit
        bottom
          vertical bottom limit
        width
          rectangle's width
        height
          rectangle's height

        Returns
        -------
           self
        """

        return self.avoid_rectangle_limits(left, left + width,
                                           bottom, bottom + height)

    def avoid_rectangle_limits(self,
                               left: float,
                               right: float,
                               bottom: float,
                               top: float,
                               ):
        """
        Add rectangles to avoid whenever ha='left', va='top', rotation=0 on write()

        Parameters
        ----------
        left: float
         left x-limit of the rectangle
        right: float
         right x-limit of the rectangle
        bottom: float
         bottom y-limit of the rectangle
        top: float
         top y-limit of the rectangle
        """
        self._rectangles.append((left, right, bottom, top))

        return self

    def reset_rectangles(self):
        """Reset avoidance rectangles"""
        self._rectangles = []

        return self

    def _check_max_leftover(self, max_height, paragraph_sep, lp,
                            left_words=None, left_paragraphs=None):
        check = max_height is not None and lp.total_height() - lp.delta_y > max_height

        if check:
            if left_words is None:
                left_words = []
            if left_paragraphs is None:
                left_paragraphs = []

            self.leftover = paragraph_sep.join([" ".join(left_words)] +
                                               left_paragraphs)

        return check

    def write(self,
              text: str,
              xy: tuple[float, float],

              width: float | None = None,
              spacing: float | None = None,
              max_height: float | None = None,

              fontname: str | None = None,
              fontsize: float | None = None,
              family: str | None = None,
              weight: str | None = None,
              style: str | None = None,

              color: str | None = None,
              rotation: float | None = None,
              justify: str | None = None,
              zorder: float | None = None,

              ha: str = 'left',
              va: str = 'top',

              avoid_left_of: avoid_specification = None,
              avoid_right_of: avoid_specification = None,
              avoid_rectangles: bool = True,

              collapse_whites: bool = True,
              paragraph_per_line: bool = False,
              ) -> tuple[list[matplotlib.artist.Artist], float]:
        """
Write text into a paragraph, storing word length in dictionary cache. Return a list to all artists

        Parameters
        ----------
        text:
          text to write
        xy:
           position to place the paragraph aligned according to ha and va
        width:
           width of paragraph
        spacing
           line spacing of paragraph
        max_height:
           maximum height of paragraph, remaining characters are stored in .leftover attribute

        fontname:
          specific fontname, if not specified then use family
        fontsize:
          use this fontsize instead of the initialized one
        family:
          family of the font
        weight:
           font weight
        style:
          font style
        color:
          color of text
        rotation:
           anticlockwise rotation
        justify:
          Line's justification
        zorder:
          Text's zorder

        ha:
          Paragraph horizontal alignment
        va:
          Paragraph vertical alignment

        avoid_left_of: avoid_specification
           tuple (x_lim, (y1, y2)). Avoid space left of x_lim between y1 and y2
        avoid_right_of: avoid_specification
          tuple (x_lim, (y1, y2)). Avoid space right of x_lim between y1 and y2

        avoid_rectangles
          whether to avoid specified rectangles (in any case, it only works if va=top, ha=left, rotation=0)
        collapse_whites
          whether multiple side-by-side withes should be considered as one
        paragraph_per_line
          if true, each new line is considered a new paragraph

        Returns
        -------
        list[Artist]

        """
        # todo: optimize max_height

        props = {'fontname': fontname,

                 'fontsize': fontsize,
                 'family': family,
                 'weight': weight,
                 'style': style,

                 'color': color,
                 'rotation': rotation,
                 'zorder': zorder,
                 }

        props = {k: v if v is not None else self._text_props[k]
                 for k, v in props.items()}
        rotation = props['rotation']

        # these affect the format of the paragraph
        if width is None:
            width = self._width
        if spacing is None:
            spacing = self._spacing
        if justify is None:
            justify = self._justify

        ax = self._axes

        # old artists are already present in the axes and won't be moved by the posteriori vertical alignment
        old_artists = list(ax.texts)

        if ax.get_ylim()[1] < ax.get_ylim()[0] or ax.get_xlim()[1] < ax.get_xlim()[0]:
            raise NotImplementedError("paraMPL.write() is only available for plots with increasing x- and y-axis")

        # word size info
        widths, height, combined_hash = self._get_widths_height(props,
                                                                words=text.split())
        space_width = widths[' ']

        # initialize position-storing object
        lp = _line_position(xy, width, height,
                            rotation, spacing, ha, justify,
                            y_to_x_ratio=get_aspect(ax))

        # add rectangles to avoid if orientation and alignment is adequate
        if va == 'top' and rotation == 0 and ha == 'left':
            if avoid_rectangles:
                lp.add_rectangles(self._rectangles)
        # if orientation is not adequate, but avoid is specified raise error
        elif avoid_left_of is not None or avoid_right_of is not None:
            raise ValueError("if using avoid areas, then va='top', ha='left', and rotation=0 are required")

        lp.add_avoids(avoid_left_of, avoid_right_of, initialize=True)

        # separate and process paragraphs one at a time.
        paragraphs, paragraph_sep = split_into_paragraphs(text,
                                                          collapse_whites=collapse_whites,
                                                          paragraph_per_line=paragraph_per_line,
                                                          )

        if props['fontname'] is None:
            del props['fontname']

        for idx_paragraph, paragraph in enumerate(paragraphs):
            words = []
            length = 0

            # if full justified add word-by-word size and when line is completed, fill with space
            if justify == 'full':
                incoming_words = paragraph.split(' ')
                for idx, word in enumerate(incoming_words):
                    if length + widths[word] > lp.width_line:
                        if len(words) > 1:
                            extra_spacing = (lp.width_line - length + space_width) / (len(words) - 1)
                        else:
                            extra_spacing = 0

                        offset = 0
                        for word_out in words:
                            x, y = lp.offset(offset=offset)
                            ax.text(x, y, word_out, **props)
                            offset += extra_spacing + space_width + widths[word_out]

                        if self._check_max_leftover(max_height, paragraph_sep, lp,
                                                    left_words=incoming_words[idx:],
                                                    left_paragraphs=paragraphs[idx_paragraph + 1:]
                                                    ):
                            return self._artists_and_vertical_align(old_artists, lp, va)

                        lp.next_line()
                        length = 0
                        words = []

                    length += widths[word] + space_width
                    words.append(word)

                # if for reaches the end (no max_height)
                else:
                    x, y = lp.offset()
                    ax.text(x, y, ' '.join(words),
                            **props)

                    if self._check_max_leftover(max_height, paragraph_sep, lp,
                                                left_paragraphs=paragraphs[idx_paragraph + 1:]
                                                ):
                        return self._artists_and_vertical_align(old_artists, lp, va)

                    lp.next_line()
                    self.leftover = ""

            # if left, right, center justified then write the whole line then move it.
            else:
                for idx, word in enumerate(paragraph.split(' ')):
                    if length + widths[word] > lp.width_line:
                        x, y = lp.offset(justified_length=length - space_width)
                        ax.text(x, y, ' '.join(words),
                                **props)
                        lp.next_line()
                        length, words = 0, []

                        if self._check_max_leftover(max_height, paragraph_sep, lp,
                                                    left_words=paragraph.split(' ')[idx+1:],
                                                    left_paragraphs=paragraphs[idx_paragraph + 1:]
                                                    ):
                            return self._artists_and_vertical_align(old_artists, lp, va)

                    length += widths[word] + space_width
                    words.append(word)

                x, y = lp.offset(justified_length=length - space_width)
                ax.text(x, y, ' '.join(words),
                        **props)

                if self._check_max_leftover(max_height, paragraph_sep, lp,
                                            left_paragraphs=paragraphs[idx_paragraph + 1:]
                                            ):
                    return self._artists_and_vertical_align(old_artists, lp, va)

                lp.next_line()

        return self._artists_and_vertical_align(old_artists, lp, va)

    def _artists_and_vertical_align(self, old_artists, lp, va):
        ax = self._axes
        # get list of artists generated for these paragraphs.
        parampl_artists = [artist for artist in ax.texts if artist not in old_artists]

        # once all paragraphs are finished, do the vertical alignment
        total_height = lp.total_height()
        delta = lp.y_to_bottom_offset()

        if va == 'top':
            for artist in parampl_artists:
                artist.set_y(artist.get_position()[1] + delta - total_height)

        elif va == 'bottom':
            if delta != 0:
                for artist in parampl_artists:
                    artist.set_y(artist.get_position()[1] + delta)

        elif va == 'center':
            for artist in parampl_artists:
                artist.set_y(artist.get_position()[1] + delta - total_height / 2)

        else:
            raise ValueError(f"invalid va '{va}'. Must be 'top', 'bottom', or 'center'")

        return parampl_artists, total_height

    def _get_widths_height(self, props,
                           words: list[str] = None,
                           ):
        text_artist = self._axes.text(0, 0, ' ',
                                      **props,
                                      )
        combined_hash = (props['fontsize'],
                         props['family'], props['fontname'],
                         props['weight'], props['style'])

        if combined_hash not in self._widths:
            text_artist.set_text(' ')
            widths: dict[str, float] = {' ': self._transformed_artist_extent(text_artist).width,
                                        '': 0,
                                        }

            text_artist.set_text('Lg')
            height = self._transformed_artist_extent(text_artist).height

            self._widths[combined_hash] = widths
            self._heights[combined_hash] = height
        else:
            widths = self._widths[combined_hash]

        if words is not None:
            for word in words:
                if word not in widths:
                    text_artist.set_text(word)
                    widths[word] = self._transformed_artist_extent(text_artist).width

        text_artist.remove()

        return self._widths[combined_hash], self._heights[combined_hash], combined_hash

    def _transformed_artist_extent(self, artist):
        extent = artist.get_window_extent(renderer=self._renderer)
        return extent.transformed(self._transform)
