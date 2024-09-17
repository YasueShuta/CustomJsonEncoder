"""Implementation of JSONEncoder
source: https://github.com/python/cpython/blob/main/Lib/json/encoder.py
"""
from sys import stderr
from .custom_serializable import CustomSerializable, CustomSerializeError

from json.encoder import (
    c_make_encoder,
    INFINITY,
    encode_basestring,
    encode_basestring_ascii,
    JSONEncoder
)
CUSTOM_CLASSES = set()
"""set of custom classes. if you add your custom classes beforehand,
CJEnc custom_classes parameter is not required."""

class CJEnc(JSONEncoder):
    """CJEnc stands for Customizable JSON Encoder."""

    def __init__(self, *, skipkeys=False, ensure_ascii=True,
            check_circular=True, allow_nan=True, sort_keys=False,
            indent=None, separators=None, default=None, custom_classes=[]):
        """Constructor for CJEnc.

        Parameters:
            custom_classes - add custom class which extends cjenc.CustomSerializable class.
                             more detail in help(cjenc.CustomSerializable).

        other parameters derives from json.JSONEncoder.
        """

        super().__init__(skipkeys=skipkeys,
                         ensure_ascii=ensure_ascii,
                         check_circular=check_circular,
                         allow_nan=allow_nan,
                         sort_keys=sort_keys,
                         indent=indent,
                         separators=separators,
                         default=default)
        self.add_custom_classes(custom_classes)

    def add_custom_classes(self, classes):
        self.custom_classes = classes
        for t in classes:
            if issubclass(t, CustomSerializable):
                CUSTOM_CLASSES.add(t)
            else:
                print(f'{t.__name__} is not CustomSerializable.', file=stderr)

    def remove_custom_classes(self, classes):
        for t in classes:
            if t in CUSTOM_CLASSES:
                CUSTOM_CLASSES.remove(t)

    def encode(self, o):
        # This is for extremely simple cases and benchmarks.
        if isinstance(o, str):
            if self.ensure_ascii:
                return encode_basestring_ascii(o)
            else:
                return encode_basestring(o)
        # This doesn't pass the iterator directly to ''.join() because the
        # exceptions aren't as detailed.  The list call should be roughly
        # equivalent to the PySequence_Fast that ''.join() would do.
        chunks = self.iterencode(o, _one_shot=(not self.custom_classes))
        if not isinstance(chunks, (list, tuple)):
            chunks = list(chunks)
        return ''.join(chunks)

    def iterencode(self, o, _one_shot=False):
        if self.check_circular:
            markers = {}
        else:
            markers = None
        if self.ensure_ascii:
            _encoder = encode_basestring_ascii
        else:
            _encoder = encode_basestring

        def floatstr(o, allow_nan=self.allow_nan,
                _repr=float.__repr__, _inf=INFINITY, _neginf=-INFINITY):
            # Check for specials.  Note that this type of test is processor
            # and/or platform-specific, so do tests which don't depend on the
            # internals.

            if o != o:
                text = 'NaN'
            elif o == _inf:
                text = 'Infinity'
            elif o == _neginf:
                text = '-Infinity'
            else:
                return _repr(o)

            if not allow_nan:
                raise ValueError(
                    "Out of range float values are not JSON compliant: " +
                    repr(o))

            return text


        if self.indent is None or isinstance(self.indent, str):
            indent = self.indent
        else:
            indent = ' ' * self.indent
        if _one_shot and c_make_encoder is not None:
            _iterencode = c_make_encoder(
                markers, self.default, _encoder, indent,
                self.key_separator, self.item_separator, self.sort_keys,
                self.skipkeys, self.allow_nan)
        else:
            _iterencode = _make_iterencode(
                markers, self.default, _encoder, indent, floatstr,
                self.key_separator, self.item_separator, self.sort_keys,
                self.skipkeys, _one_shot)
        return _iterencode(o, 0)

def _make_iterencode(markers, _default, _encoder, _indent, _floatstr,
        _key_separator, _item_separator, _sort_keys, _skipkeys, _one_shot,
        ## HACK: hand-optimized bytecode; turn globals into locals
        ValueError=ValueError,
        dict=dict,
        float=float,
        id=id,
        int=int,
        isinstance=isinstance,
        list=list,
        str=str,
        tuple=tuple,
        _intstr=int.__repr__,
    ):

    def _iterencode_list(lst, _current_indent_level, _local_separator=_item_separator):
        if not lst:
            yield '[]'
            return
        if markers is not None:
            markerid = id(lst)
            if markerid in markers:
                raise ValueError("Circular reference detected")
            markers[markerid] = lst
        buf = '['
        if _indent is not None:
            _current_indent_level += 1
            newline_indent = '\n' + _indent * _current_indent_level
            separator = _local_separator + newline_indent
            buf += newline_indent
        else:
            newline_indent = None
            separator = _local_separator
        for i, value in enumerate(lst):
            if i:
                buf = separator
            try:
                if isinstance(value, tuple(CUSTOM_CLASSES)):
                    yield from value.get_yield(_current_indent_level=_current_indent_level, default_iterencode=_iterencode)
                elif isinstance(value, str):
                    yield buf + _encoder(value)
                elif value is None:
                    yield buf + 'null'
                elif value is True:
                    yield buf + 'true'
                elif value is False:
                    yield buf + 'false'
                elif isinstance(value, int):
                    # Subclasses of int/float may override __repr__, but we still
                    # want to encode them as integers/floats in JSON. One example
                    # within the standard library is IntEnum.
                    yield buf + _intstr(value)
                elif isinstance(value, float):
                    # see comment above for int
                    yield buf + _floatstr(value)
                else:
                    yield buf
                    if isinstance(value, (list, tuple)):
                        chunks = _iterencode_list(value, _current_indent_level, _local_separator)
                    elif isinstance(value, dict):
                        chunks = _iterencode_dict(value, _current_indent_level, _local_separator)
                    else:
                        chunks = _iterencode(value, _current_indent_level, _local_separator)
                    yield from chunks
            except GeneratorExit:
                raise
            except BaseException as exc:
                exc.add_note(f'when serializing {type(lst).__name__} item {i}')
                raise
        if newline_indent is not None:
            _current_indent_level -= 1
            yield '\n' + _indent * _current_indent_level
        yield ']'
        if markers is not None:
            del markers[markerid]

    def _iterencode_dict(dct, _current_indent_level, _local_separator=_item_separator):
        if not dct:
            yield '{}'
            return
        if markers is not None:
            markerid = id(dct)
            if markerid in markers:
                raise ValueError("Circular reference detected")
            markers[markerid] = dct
        yield '{'
        if _indent is not None:
            _current_indent_level += 1
            newline_indent = '\n' + _indent * _current_indent_level
            item_separator = _local_separator + newline_indent
            yield newline_indent
        else:
            newline_indent = None
            item_separator = _local_separator
        first = True
        if _sort_keys:
            items = sorted(dct.items())
        else:
            items = dct.items()
        for key, value in items:
            if isinstance(key, str):
                pass
            # JavaScript is weakly typed for these, so it makes sense to
            # also allow them.  Many encoders seem to do something like this.
            elif isinstance(key, float):
                # see comment for int/float in _make_iterencode
                key = _floatstr(key)
            elif key is True:
                key = 'true'
            elif key is False:
                key = 'false'
            elif key is None:
                key = 'null'
            elif isinstance(key, int):
                # see comment for int/float in _make_iterencode
                key = _intstr(key)
            elif _skipkeys:
                continue
            else:
                raise TypeError(f'keys must be str, int, float, bool or None, '
                                f'not {key.__class__.__name__}')
            if first:
                first = False
            else:
                yield item_separator
            yield _encoder(key)
            yield _key_separator
            try:
                if isinstance(value, tuple(CUSTOM_CLASSES)):
                    yield from value.get_yield("", current_indent_level=_current_indent_level, default_iterencode=_iterencode)
                elif isinstance(value, str):
                    yield _encoder(value)
                elif value is None:
                    yield 'null'
                elif value is True:
                    yield 'true'
                elif value is False:
                    yield 'false'
                elif isinstance(value, int):
                    # see comment for int/float in _make_iterencode
                    yield _intstr(value)
                elif isinstance(value, float):
                    # see comment for int/float in _make_iterencode
                    yield _floatstr(value)
                else:
                    if isinstance(value, (list, tuple)):
                        chunks = _iterencode_list(value, _current_indent_level, _local_separator)
                    elif isinstance(value, dict):
                        chunks = _iterencode_dict(value, _current_indent_level, _local_separator)
                    else:
                        chunks = _iterencode(value, _current_indent_level, _local_separator)
                    yield from chunks
            except GeneratorExit:
                raise
            except BaseException as exc:
                exc.add_note(f'when serializing {type(dct).__name__} item {key!r}')
                raise
        if newline_indent is not None:
            _current_indent_level -= 1
            yield '\n' + _indent * _current_indent_level
        yield '}'
        if markers is not None:
            del markers[markerid]

    def _iterencode(o, _current_indent_level, _local_separator=_item_separator):
        if isinstance(o, tuple(CUSTOM_CLASSES)):
            yield from o.get_yield("", current_indent_level=_current_indent_level, default_iterencode=_iterencode)
        elif isinstance(o, str):
            yield _encoder(o)
        elif o is None:
            yield 'null'
        elif o is True:
            yield 'true'
        elif o is False:
            yield 'false'
        elif isinstance(o, int):
            # see comment for int/float in _make_iterencode
            yield _intstr(o)
        elif isinstance(o, float):
            # see comment for int/float in _make_iterencode
            yield _floatstr(o)
        elif isinstance(o, (list, tuple)):
            yield from _iterencode_list(o, _current_indent_level, _local_separator)
        elif isinstance(o, dict):
            yield from _iterencode_dict(o, _current_indent_level, _local_separator)
        else:
            if markers is not None:
                markerid = id(o)
                if markerid in markers:
                    raise ValueError("Circular reference detected")
                markers[markerid] = o
            newobj = _default(o)
            try:
                yield from _iterencode(newobj, _current_indent_level, _local_separator)
            except GeneratorExit:
                raise
            except BaseException as exc:
                exc.add_note(f'when serializing {type(o).__name__} object')
                raise
            if markers is not None:
                del markers[markerid]
    return _iterencode