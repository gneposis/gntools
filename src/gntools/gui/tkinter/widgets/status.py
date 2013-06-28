"""
Tkinter status report widgets.
"""
# Full license text:
# ------------------------------------------------------------------------
#              DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#                        Version 2, December 2004
#
# Copyright (C) 2004 Sam Hocevar <sam@hocevar.net>
#
# Everyone is permitted to copy and distribute verbatim or modified copies
# of this license document, and changing it is allowed as long as the name
# is changed.
#
#              DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#    TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION
#
# 0. You just DO WHAT THE FUCK YOU WANT TO.
# ------------------------------------------------------------------------
import sys
import tkinter

class StdoutToWidget:
    '''
    Retrieves sys.stdout and show write calls also in a tkinter
    widget. It accepts widgets which have a "text" config and defines
    their width and height in characters. It also accepts Text widgets.
    Use stop() to stop retrieving.

    You can manage output height by using the keyword argument. By default
    the class tries to get widget\'s height configuration and use that. If
    that fails it sets self.height to None which you can also do manually.
    In this case the output will not be trimmed. However if you do not
    manage your widget, it can grow vertically hard by getting more and
    more inputs.
    '''

    # Inspired by Jesse Harris and Stathis
    # http://stackoverflow.com/a/10846997/2334951
    # http://stackoverflow.com/q/14710529/2334951

    # TODO: horizontal wrapping
    #       make it a widget decorator (if possible)
    #       height management for Text widget mode

    def __init__(self, widget, height='default', width='default'):
        self._content = []
        self.defstdout = sys.stdout
        self.widget = widget

        if height == 'default':
            try:
                self.height = widget.cget('height')
            except:
                self.height = None
        else:
            self.height = height
        if width == 'default':
            try:
                self.width = widget.cget('width')
            except:
                self.width = None
        else:
            self.width = width   

    def flush(self):
        '''
        Frame sys.stdout's flush method.
        '''
        self.defstdout.flush()

    def write(self, string, end=None):
        '''
        Frame sys.stdout's write method. This method puts the input
        strings to the widget.
        '''

        if string is not None:
            self.defstdout.write(string)
            try:
                last_line_last_char = self._content[-1][-1]
            except IndexError:
                last_line_last_char = '\n'
            else:
                if last_line_last_char == '\n':
                    self._content[-1] = self._content[-1][:-1]

            if last_line_last_char != '\n' and string.startswith('\r'):
                self._content[-1] = string[1:]
            elif last_line_last_char != '\n':
                self._content[-1] += string
            elif last_line_last_char == '\n' and string.startswith('\r'):
                self._content.append(string[1:])
            else:
                self._content.append(string)

        if hasattr(self.widget, 'insert') and hasattr(self.widget, 'see'):
            self._write_to_textwidget()
        else:
            self._write_to_regularwidget(end)

    def _write_to_regularwidget(self, end):
        if self.height is None:
            self.widget.config(text='\n'.join(self.content))
        else:
            if not end:
                content = '\n'.join(self.content[-self.height:])
            else:
                content = '\n'.join(self.content[-self.height+end:end])
            self.widget.config(text=content)

    def _write_to_textwidget(self):
        self.widget.insert('end', '\n'.join(self.content))
        self.widget.see('end')        

    def start(self):
        '''
        Starts retrieving.
        '''
        sys.stdout = self

    def stop(self):
        '''
        Stops retrieving.
        '''
        sys.stdout = self.defstdout

    @property
    def content(self):
        c = []
        for li in self._content:
            c.extend(li.split('\n'))

        if not self.width:
            return c
        else:
            result = []
            for li in c:
                while len(li) > self.width:
                    result.append(li[:self.width])
                    li = li[self.width:]
                result.append(li)
            return result

    @content.setter
    def content(self, string):
        self._content = string.split('\n')

    @property
    def errors(self):
        return self.defstdout.errors

    @property
    def encoding(self):
        return self.defstdout.encoding

# From somwhere on the net
class ReadOnlyText(tkinter.Text):
    def __init__(self, *args, **kwargs):
        from idlelib.WidgetRedirector import WidgetRedirector
        tkinter.Text.__init__(self, *args, **kwargs)
        self.redirector = WidgetRedirector(self)
        self.insert = \
            self.redirector.register("insert", lambda *args, **kw: "break")
        self.delete = \
            self.redirector.register("delete", lambda *args, **kw: "break")