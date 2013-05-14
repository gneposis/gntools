import tkinter

# code from Mark Lutz -- Programming Python (4th edition)
class List(tkinter.Frame):
    def __init__(self, parent, height=6):
        tkinter.Frame.__init__(self, parent)
        self.make_widgets(height)

    def make_widgets(self, height, selectmode=tkinter.EXTENDED):
        sbar = tkinter.Scrollbar(self)
        self.list_ = tkinter.Listbox(self,
                                    relief=tkinter.SUNKEN,
                                    selectmode=selectmode,
                                    exportselection=0,
                                    activestyle='none',
                                    height=height,
                                    width=0)
        sbar.config(command=self.list_.yview)
        self.list_.config(yscrollcommand=sbar.set)
        sbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self.list_.pack(side=tkinter.LEFT, 
                       expand=tkinter.YES, 
                       fill=tkinter.BOTH)


    def make_options(self, options, autosort=True):
        self.list_.delete(0, tkinter.END)
        pos = 0
        for label in options:
            self.list_.insert(pos, label)
            pos += 1

       

if __name__ == '__main__':
    options = (('Lumberjack {}'.format(x)) for x in range(1, 21))
    List(options).mainloop()