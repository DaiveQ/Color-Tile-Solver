from time import sleep
import pyscreenshot
import win32api
from enum import Enum

import win32con

X_TILES = 23
Y_TILES = 15

grid = []

tl_x, tl_y = -1, -1
br_x, br_y = -1, -1

blk_x_offset = -1
blk_y_offset = -1
blk_x_size = -1
blk_y_size = -1

CLR_TOLERANCE = 40


# color enum
class Color(Enum):
	UNKNOWN = -1
	BLANK = 1
	BLANK_A = 0xf5f7f7
	BLANK_B = 0xebeded
	PINK = 0xfd89ff
	RED = 0xfd7676
	GREEN = 0x03cd05
	LIGHT_BLUE = 0x66cccc
	BLUE = 0x076bff
	YELLOW = 0xccce6d
	ORANGE = 0xfda011
	PURPLE = 0xcc6dce
	GREY = 0xbcbebe
	BROWN = 0xca6702


def get_mouse_pos():
	# intercept tilda
	if win32api.GetAsyncKeyState(192):
		x, y = win32api.GetCursorPos()
		sleep(0.5)
		return x, y
	else:
		return -1, -1


def initialize_positions():
	global tl_x, tl_y, br_x, br_y
	while tl_x == -1 and tl_y == -1:
		tl_x, tl_y = get_mouse_pos()

	sleep(.1)

	while br_x == -1 and br_y == -1:
		br_x, br_y = get_mouse_pos()


def initialize_blk_values():
	global blk_x_offset, blk_y_offset, blk_x_size, blk_y_size
	blk_x_size = (br_x - tl_x) / X_TILES
	blk_y_size = (br_y - tl_y) / Y_TILES
	blk_x_offset = blk_x_size / 2
	blk_y_offset = blk_y_size / 2


def get_screen():
	return pyscreenshot.grab(bbox=(tl_x, tl_y, br_x, br_y))


def is_color_equal(clr_a, clr_b):
	# split into 3 channels
	a_r = (0xff0000 & clr_a) >> 16
	a_g = (0x00ff00 & clr_a) >> 8
	a_b = 0x0000ff & clr_a

	b_r = (0xff0000 & clr_b) >> 16
	b_g = (0x00ff00 & clr_b) >> 8
	b_b = 0x0000ff & clr_b

	# return if all channels are within tolerance
	return abs(a_r - b_r) < CLR_TOLERANCE and abs(a_g - b_g) < CLR_TOLERANCE and abs(a_b - b_b) < CLR_TOLERANCE


def initialize_grid(img):
	for x in range(X_TILES):
		new_col = []
		for y in range(Y_TILES):
			new_col.append(get_color(img, x, y))
		grid.append(new_col)


def get_color(img, x, y):
	x, y = conv_grid_to_pos(x, y)
	r, g, b = img.getpixel((x, y))
	clr = (r << 16) + (g << 8) + b

	if is_color_equal(clr, Color.BLANK_A.value) or is_color_equal(clr, Color.BLANK_B.value):
		return Color.BLANK
	elif is_color_equal(clr, Color.PINK.value):
		return Color.PINK
	elif is_color_equal(clr, Color.RED.value):
		return Color.RED
	elif is_color_equal(clr, Color.GREEN.value):
		return Color.GREEN
	elif is_color_equal(clr, Color.LIGHT_BLUE.value):
		return Color.LIGHT_BLUE
	elif is_color_equal(clr, Color.BLUE.value):
		return Color.BLUE
	elif is_color_equal(clr, Color.YELLOW.value):
		return Color.YELLOW
	elif is_color_equal(clr, Color.ORANGE.value):
		return Color.ORANGE
	elif is_color_equal(clr, Color.PURPLE.value):
		return Color.PURPLE
	elif is_color_equal(clr, Color.GREY.value):
		return Color.GREY
	elif is_color_equal(clr, Color.BROWN.value):
		return Color.BROWN
	else:
		return Color.UNKNOWN


def conv_grid_to_pos(grid_x, grid_y):
	return int(grid_x * blk_x_size + blk_x_offset), int(grid_y * blk_y_size + blk_y_offset)


def check_if_valid(x, y):
	if grid[x][y] != Color.BLANK:
		return False

	found_colors = []
	pos = []
	repeat_colors = []

	for i in range(x - 1, -1, -1):
		clr = grid[i][y]
		if clr != Color.BLANK:
			if clr in found_colors:
				repeat_colors.append(clr)
			found_colors.append(clr)
			pos.append((i, y))
			break

	for i in range(x + 1, X_TILES):
		clr = grid[i][y]
		if clr != Color.BLANK:
			if clr in found_colors:
				repeat_colors.append(clr)
			found_colors.append(clr)
			pos.append((i, y))
			break

	for i in range(y - 1, -1, -1):
		clr = grid[x][i]
		if clr != Color.BLANK:
			if clr in found_colors:
				repeat_colors.append(clr)
			found_colors.append(clr)
			pos.append((x, i))
			break

	for i in range(y + 1, Y_TILES):
		clr = grid[x][i]
		if clr != Color.BLANK:
			if clr in found_colors:
				repeat_colors.append(clr)
			found_colors.append(clr)
			pos.append((x, i))
			break

	for i in range(len(found_colors)):
		if found_colors[i] in repeat_colors:
			grid[pos[i][0]][pos[i][1]] = Color.BLANK

	if len(repeat_colors) == 0:
		return False
	else:
		return True


def click(grid_x, grid_y):
	x, y = conv_grid_to_pos(grid_x, grid_y)
	win32api.SetCursorPos((tl_x + x, tl_y + y))
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
	sleep(.1)
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)


# draws crosshair like grid indicating which pixels are chosen
def debug_show_targets(img):
	img_copy = img.copy()
	for y in range(Y_TILES):
		# iterate through entire image
		for x in range(br_x - tl_x - 1):
			a, b = conv_grid_to_pos(0, y)
			img_copy.putpixel((x, b), (0, 0, 0))

	for x in range(X_TILES):
		# iterate through entire image
		for y in range(br_y - tl_y - 1):
			a, b = conv_grid_to_pos(x, 0)
			img_copy.putpixel((a, y), (0, 0, 0))
	img_copy.show()


def debug_show_img(img):
	img.show()

def greedy_solve():
	print("Waiting for initialization...")
	initialize_positions()
	initialize_blk_values()
	img = get_screen()
	initialize_grid(img)

	print("Starting...")
	while True:
		for y in range(Y_TILES):
			for x in range(X_TILES):
				if win32api.GetAsyncKeyState(win32con.VK_ESCAPE):
					print("Stopping...")
					global grid, tl_x, tl_y, br_x, br_y, blk_x_size, blk_y_size, blk_x_offset, blk_y_offset
					grid = []
					tl_x = -1
					tl_y = -1
					br_x = -1
					br_y = -1
					blk_x_size = -1
					blk_y_size = -1
					return
				if check_if_valid(x, y):
					click(x, y)



if __name__ == '__main__':
	while True:
		greedy_solve()