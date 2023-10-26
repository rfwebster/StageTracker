import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, Normalize
from matplotlib.patches import Circle
plt.style.use('dark_background')

import numpy as np

try:
    _online = True
    from PyJEM import TEM3
except ImportError:
    _online = False
    from PyJEM.offline import TEM3

class Coord:
    def __init__(self):
        self.CurrentX = 0
        self.CurrentY = 0
        self.snake = []
        self.snake.append([self.CurrentX, self.CurrentY])

    def append_snake(self):
        self.snake.append([self.CurrentX/1000, self.CurrentY/1000])



class App:
    def __init__(self, master):
        self.master = master
        self.coord = Coord()

        self.setup_ui()

        self.fig = Figure(figsize=(5, 5), dpi=100)
        self.ax = self.fig.add_subplot(111)

        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        
        self.lim = 200

        self.ax.set_xlim(-self.lim, self.lim)
        self.ax.set_ylim(-self.lim, self.lim)
        self.ax.set_aspect('equal')

        self.ax.set_title('Snake')

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        
        self.current_plot = self.ax.scatter(self.coord.CurrentX/1000, self.coord.CurrentY/1000,
                                             label="Current", c="yellow", marker="x")
        self.ax.legend(loc='upper left', fontsize="small")
        
        self.snake_lines = []
        self.snake_colors = []
        self.snake_age = []
        self.cmap = ListedColormap(['blue', 'green', 'yellow', 'orange', 'red'])
        self.norm = Normalize(vmin=0, vmax=50)

        self.circle1 = Circle((0, 0), radius=self.lim/4, color='lawngreen', alpha=0.5, fill=False)
        self.circle2 = Circle((0, 0), radius=self.lim/2, color='lawngreen', alpha=0.5, fill=False)
        self.circle3 = Circle((0, 0), radius=3*self.lim/4, color='lawngreen', alpha=0.5, fill=False)
        self.circle4 = Circle((0, 0), radius=self.lim, color='lawngreen', alpha=0.5, fill=False)

        self.ax.add_patch(self.circle1)
        self.ax.add_patch(self.circle2)
        self.ax.add_patch(self.circle3)
        self.ax.add_patch(self.circle4)
        
        self.update_plot()
    
    def setup_ui(self):
        self.frame = tk.Frame(self.master)
        self.frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.move_Button = tk.Button(self.frame, text="Move Random", command=self._move_random)
        self.move_Button.pack(side=tk.LEFT)
        
        self.SpinBoxX = tk.Spinbox(self.frame, from_=0, to=1000, increment=1, width=5)
        self.SpinBoxX.pack(side=tk.RIGHT)
        self.SpinBoxX.bind('<Return>', self._setlim)  # bind Return key to _setlim method

        self.limit_button = tk.Button(self.frame, text="Set Limit:", command=self._setlim)
        self.limit_button.pack(side=tk.RIGHT)


        self.NumX = tk.Label(self.frame, text="0.0")
        self.NumX.pack(side=tk.LEFT)
        self.NumY = tk.Label(self.frame, text="0.0")
        self.NumY.pack(side=tk.LEFT)
        self.update_Button = tk.Button(self.frame, text="Update", command=self._update)
        self.update_Button.pack(side=tk.LEFT)


    def update_plot(self):
        """
        Function to update the plot with the current position of the stage
        and the snake
        """
        # self.ax.cla()
        self.current_plot.set_offsets(np.array([self.coord.CurrentX/1000, self.coord.CurrentY/1000]))

        arr = np.array(self.coord.snake)
        print(arr.T)

        try:
            arr = arr.T
            x = arr[0]
            y = arr[1]
            z = np.linspace(0, 10, len(x))
            points = np.array([x, y]).T.reshape(-1, 1, 2)
            segments = np.concatenate([points[:-1], points[1:]], axis=1)
            norm = plt.Normalize(z.min(), z.max())
            lc = LineCollection(segments, cmap='autumn', norm=norm)
            # Set the values used for colormapping
            lc.set_array(z)
            lc.set_linewidth(0.5)
            line = self.ax.add_collection(lc)
        except IndexError:
            pass
        self.canvas.draw()

    ######################################################################################
    #
    # UI Buttons amd functions etc
    #
    ######################################################################################

    def _move_random(self):
        x = np.random.randint(-100000,100000)
        y = np.random.randint(-100000,100000)
        stage.SetX(x)
        stage.SetY(y)
        self._get_current_position()

    def _setlim(self, lim = None):
        x = float(self.SpinBoxX.get())
        self.lim = int(x)
        self.ax.set_xlim(-self.lim, self.lim)
        self.ax.set_ylim(-self.lim, self.lim)
        self.circle1.set_radius(self.lim/4)
        self.circle2.set_radius(self.lim/2)
        self.circle3.set_radius(3*self.lim/4)
        self.circle4.set_radius(self.lim)
        self.update_plot()

    def _update(self):
        #self._get_current_position()
        self.NumX.configure(text=self.coord.CurrentX/1000)
        self.NumY.configure(text=self.coord.CurrentY/1000)
        self.update_plot()
        #QTest.qWait(1000)

    def _get_current_position(self):
        print("getting current position")
        pos = stage.GetPos()
        print(pos[0], pos[1])
        self.coord.CurrentX, self.coord.CurrentY = pos[0], pos[1]
        self.coord.append_snake()
        self._update()

if __name__ == "__main__":
    stage = TEM3.Stage3()
    root = tk.Tk()
    app = App(root)
    root.mainloop()