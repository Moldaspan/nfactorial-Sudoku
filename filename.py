import pygame
import random
import json
pygame.init()
pygame.display.set_caption("Sudoku")
window = pygame.display.set_mode([710, 600])
font = pygame.font.Font('freesansbold.ttf', 32)
font2 = pygame.font.Font('freesansbold.ttf', 26)
smallFont = pygame.font.Font('freesansbold.ttf', 10)
currentNum = -1
run = True
TIMER_DURATION_MS = 360000 
start_time = pygame.time.get_ticks()  # Get the current time in milliseconds
easy_game = [
    [0, 0, 0, 8, 0, 3, 0, 0, 1],
    [0, 8, 3, 2, 0, 4, 0, 0, 7],
    [0, 7, 0, 0, 9, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0, 0, 6, 8],
    [0, 6, 2, 0, 0, 0, 1, 7, 0],
    [7, 3, 0, 0, 0, 0, 4, 0, 0],
    [0, 0, 0, 0, 6, 0, 0, 1, 0],
    [9, 0, 0, 3, 0, 1, 5, 2, 0],
    [3, 0, 0, 4, 0, 5, 0, 0, 0]
]

medium_game = [
    [0, 3, 0, 0, 9, 0, 0, 6, 0],
    [0, 0, 0, 5, 1, 0, 9, 0, 0],
    [0, 5, 0, 0, 8, 0, 0, 0, 4],
    [1, 0, 5, 0, 0, 0, 0, 0, 8],
    [0, 0, 9, 0, 3, 0, 4, 0, 0],
    [4, 0, 0, 0, 0, 0, 5, 0, 7],
    [5, 0, 0, 0, 6, 0, 0, 7, 0],
    [0, 0, 3, 0, 2, 7, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 9, 0]
]
hard_game = [
    [0, 0, 0, 0, 7, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 6, 0, 0, 4],
    [4, 9, 0, 0, 0, 0, 7, 0, 0],
    [0, 0, 0, 0, 0, 2, 0, 0, 0],
    [0, 6, 0, 8, 0, 0, 5, 0, 0],
    [5, 0, 0, 0, 1, 0, 0, 0, 0],
    [8, 0, 0, 0, 0, 0, 9, 2, 0],
    [0, 0, 0, 0, 0, 7, 0, 0, 0],
    [0, 0, 6, 0, 0, 0, 0, 0, 0]
]
temp = easy_game
class Cell:
	DEFAULT_BG = (255, 255, 255)
	HIGHLIGHT_BG = (240, 240, 240)
	DARK_HIGHLIGHT_BG = (220, 220, 220)
	SELECTED_BG = (200, 200, 200)
	DEFAULT_TEXT = (83, 147, 181)
	INVALID_TEXT = (199, 58, 102)
	GIVEN_TEXT = (100, 100, 100)

	def __init__(self, x, y, row, col):
		self.x = x
		self.y = y
		self.row = row
		self.col = col
		self.value = 0
		self.size = 50
		self.bgColor = self.DEFAULT_BG
		self.textColor = self.DEFAULT_TEXT
		self.notes = []

	def highlight(self):
		if self.bgColor != self.SELECTED_BG:
			self.bgColor = self.HIGHLIGHT_BG

	def darkHighlight(self):
		if self.bgColor != self.SELECTED_BG:
			self.bgColor = self.DARK_HIGHLIGHT_BG


	def unhighlight(self):
		self.bgColor = self.DEFAULT_BG

	def setSelected(self):
		self.bgColor = self.SELECTED_BG

	def resetTextColor(self):
		self.textColor = self.DEFAULT_TEXT

	def setInvalid(self):
		self.textColor = self.INVALID_TEXT

	def setGiven(self):
		self.textColor = self.GIVEN_TEXT

	def setValue(self, value):
		self.value = value
		text_surface = self.font.render(str(self.value), True, (0,0,0))
		text_rect = text_surface.get_rect(center=self.rect.center)
		pygame.draw.rect(window, (255,255,255), self.rect)
		window.blit(text_surface, text_rect)

class Board:
	def __init__(self):
		self.backtracks = 0
		self.solveSteps = []
		self.implications = []

		self.solved = False
		self.cellArray = []
		for i in range(9):
			self.cellArray.append([])
			for j in range(9):
				self.cellArray[i].append(Cell(j*50+130, i*50+35, i, j)) 
	def draw(self, window):
		global currentNum
		global font
		for i in range(9):
			for j in range(9):
				cell = self.cellArray[i][j]
				cell.rect = pygame.Rect(cell.x, cell.y, cell.size, cell.size)
				pygame.draw.rect(window, (200, 200, 200), cell.rect, 2)
				if str(currentNum) == str(cell.value):
					cell.darkHighlight()
				pygame.draw.rect(window, cell.bgColor, (cell.x+2, cell.y+2, cell.size-3, cell.size-3))
				if cell.value > 0:
					text = font.render(str(cell.value), True, cell.textColor)
					window.blit(text, (cell.rect.x+(cell.rect.width/2)-text.get_width() // 2, cell.rect.y+2+(cell.rect.height/2)-text.get_height() // 2))

				cellNotes = ""
				for note in cell.notes:
					cellNotes += str(note)
				if cellNotes != "":
					noteText = smallFont.render(cellNotes, True, cell.GIVEN_TEXT)
					window.blit(noteText, (cell.rect.x+(cell.rect.width/2)-noteText.get_width() // 2, cell.rect.y+2+(cell.rect.height/2)-noteText.get_height() // 2))

		for i in range(3):
			for j in range(3):
				pygame.draw.rect(window, (100, 100, 100), (i*150+130, j*150+35, 50*3, 50*3), 2)

	def updateBoard(self, mouseX, mouseY):
		global currentNum
		self.clearHighlights()
		for i in range(9):
			for j in range(9):
				cell = self.cellArray[i][j]

				if cell.x < mouseX and mouseX < cell.x + cell.size and cell.y < mouseY and mouseY < cell.y + cell.size:

					for item in self.getRow(i):
						item.highlight()
					for item in self.getCol(j):
						item.highlight()
					for item in self.getSector(i, j):
						item.highlight()
					if cell.textColor != cell.GIVEN_TEXT:
						cell.resetTextColor()
						for item in self.getRow(i):
							if item.value == currentNum and(item.row != cell.row or item.col != cell.col):
								cell.setInvalid()
						for item in self.getCol(j):
							if item.value == currentNum and (item.row != cell.row or item.col != cell.col):
								cell.setInvalid()
						for item in self.getSector(i, j):
							if item.value == currentNum and (item.row != cell.row or item.col != cell.col):
								cell.setInvalid()

						if currentNum == "X":
							cell.value = 0
						elif currentNum > 0:
							cell.value = currentNum

						if self.isComplete():
							self.solved = True
							print("solved")
							end_time = pygame.time.get_ticks()
							time_taken = (end_time - start_time) / 1000
							f = open('results.json')
							results = json.load(f)
							if time_taken > results[temp]:
								results[temp] = time_taken
							with open('results.json', 'w') as f:
								json.dump(results, f)
					else:
						print("can't change text of given cell")

					cell.setSelected()

					break

	def loadBoard(self, values):
		if len(values) == 9 and len(values[0]) == 9:
			for i in range(9):
				for j in range(9):
					self.cellArray[i][j].value = values[i][j]
					if values[i][j] != 0:
						self.cellArray[i][j].setGiven()
		else:
			print("error: board size is not valid")

	def isValid(self, i, j, n):
		for item in self.getRow(i):
			if item.value == n and(item.row != i or item.col != j):
				return False
		for item in self.getCol(j):
			if item.value == n and (item.row != i or item.col != j):
				return False
		for item in self.getSector(i, j):
			if item.value == n and (item.row != i or item.col != j):
				return False

		return True

	def isComplete(self):
		complete = True
		for i in range(9):
			for j in range(9):
				cell = self.cellArray[i][j]
				if cell.value == 0 or cell.textColor == cell.INVALID_TEXT:
					complete = False
					break
		return complete

	def getNextValidCell(self):
		for i in range(9):
			for j in range(9):
				if self.cellArray[i][j].value == 0:
					return i, j
		return -1, -1

	def makeImplications(self):
		for i in range(9):
			for j in range(9):
				self.takeNotes()
				cell = self.cellArray[i][j]
				if len(cell.notes) == 1:
					if self.isValid(i, j, cell.notes[0]):
						self.cellArray[i][j].value = cell.notes[0]
						self.solveSteps.insert(0, [i, j, cell.notes[0]])
						self.implications.insert(0, [i, j])

	def solve(self):
		i, j = self.getNextValidCell()
		if i == -1:
			print(self.backtracks)
			self.printBoard()
			return True
		for n in range(1, 10):
			if self.isValid(i, j, n):
				self.cellArray[i][j].value = n
				self.solveSteps.insert(0, [i, j, n])

				self.makeImplications()
					
				if self.solve():
					return True
				self.backtracks += 1
				self.cellArray[i][j].value = 0
				self.solveSteps.insert(0, [i, j, 0])

				for imp in self.implications:
					i, j = imp
					self.cellArray[i][j].value = 0
					self.solveSteps.insert(0, [i, j, 0])
				self.implications = []
				
		return False 

	def clearHighlights(self):
		for i in range(9):
			for j in range(9):
				cell = self.cellArray[i][j]
				cell.unhighlight()

	def takeNotes(self):
		for i in range(9):
			for j in range(9):
				cell = self.cellArray[i][j]
				cell.notes = []
				if cell.value == 0:
					cellRow = self.toArray(self.getRow(cell.row))
					cellCol = self.toArray(self.getCol(cell.col))
					cellSector = self.toArray(self.getSector(cell.row, cell.col))
					for x in range(10):
						if not x in cellRow and not x in cellCol and not x in cellSector:
							cell.notes.append(x)

	def getRow(self, i):
		row = []
		for j in range(9):
			row.append(self.cellArray[i][j])
		return self.cellArray[i]

	def getCol(self, j):
		col = []
		for i in range(9):
			col.append(self.cellArray[i][j])
		return col

	def getSector(self, i, j):
		sector_row = 6
		sector_col = 6
		if i < 3:
			sector_row = 0
		elif i < 6:
			sector_row = 3

		if j < 3:
			sector_col = 0
		elif j < 6:
			sector_col = 3

		sectorCells = []
		for x in range(3):
			for y in range(3):
				sectorCells.append(self.cellArray[x + sector_row][y + sector_col])
		return sectorCells

	def toArray(self, cells):
		arr = []
		for cell in cells:
			arr.append(cell.value)
		return arr

	def printBoard(self):
		for i in range(9):
			print(self.toArray(self.getRow(i)))

class Button:
	def __init__(self, x, y, w, h, value):
		self.x = x
		self.y = y
		self.value = value
		self.width = w
		self.height = h
		self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

	def draw(self, window):
		global currentNum
		global font
		pygame.draw.rect(window, (200, 200, 200), self.rect, 2)

		color = (83, 147, 181)
		if currentNum == self.value:
			color = (199, 58, 102)
		text = font.render(str(self.value), True, color)
		window.blit(text, (self.rect.x+(self.rect.width/2)-text.get_width() // 2, self.rect.y+2+(self.rect.height/2)-text.get_height() // 2))
# end of button class

def draw_window(window):
	window.fill((255, 255, 255)) # clears background
	board.draw(window) # draws sudoku board
	solveBtn.draw(window)
	text = font2.render("1-Easy     2-Medium     3-Hard", True, (83, 147, 181))
	window.blit(text, (170,0))
	elapsed_time = pygame.time.get_ticks() - start_time
	if elapsed_time >= TIMER_DURATION_MS:
		run = False
	# draws buttons
	tt = TIMER_DURATION_MS - elapsed_time
	text2 = font2.render(f'', True, (255,0,0))
	tt = TIMER_DURATION_MS - elapsed_time
	minutes = tt // 60000
	seconds = (tt // 1000) % 60
	text2 = font2.render(f'{minutes:02}:{seconds:02}', True, (255,0,0))
	window.blit(text2, (10,0))
	for button in buttons:
		button.draw(window)

	# refreshes display
	pygame.display.update()




# creates board and loads preset sudoku game
board = Board()
board.loadBoard(temp)
buttons = []
for i in range(9):
	buttons.append(Button(i*50+50, 515, 50, 50, i+1))
buttons.append(Button(9*50+50, 515, 50, 50, "X"))

# adds a solve button
solveBtn = Button(10*50+50, 515, 110, 50, "solve")
solvePuzzle = False

# clears notes
for i in range(9):
	for j in range(9):
		board.cellArray[i][j].notes = []


while run:
	pygame.time.delay(100)
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			quit()
			run = False
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_2:
				if temp != medium_game:
					temp = medium_game
				board.loadBoard(temp)
			if event.key == pygame.K_3:
				if temp != hard_game:
					temp = hard_game
				board.loadBoard(temp)
			if event.key == pygame.K_1:
				if temp != easy_game:
					temp = easy_game
				board.loadBoard(temp)
									
		if event.type == pygame.MOUSEBUTTONDOWN:
			mouse_x, mouse_y = event.pos
			board.updateBoard(mouse_x, mouse_y)
			if solveBtn.x < mouse_x and mouse_x < solveBtn.x + solveBtn.width:
				if solveBtn.y < mouse_y and mouse_y < solveBtn.y + solveBtn.height:
					board.loadBoard(temp)
					board.solve()
					board.loadBoard(temp)

					solvePuzzle = True

					if board.backtracks < 100:
						animationSpeed = 30
					elif board.backtracks < 300:
						animationSpeed = 40
					elif board.backtracks < 600:
						animationSpeed = 60
					elif board.backtracks < 900:
						animationSpeed = 90
					elif board.backtracks < 1400:
						animationSpeed = 130
					elif board.backtracks < 2000:
						animationSpeed = 180
					elif board.backtracks < 3000:
						animationSpeed = 250
					else:
						animationSpeed = 500

			for button in buttons:
				if button.x < mouse_x and mouse_x < button.x + button.width:
					if button.y < mouse_y and mouse_y < button.y + button.height:
						if currentNum != button.value:
							currentNum = button.value
						else:
							currentNum = -1
	elapsed_time = pygame.time.get_ticks() - start_time
	if elapsed_time >= TIMER_DURATION_MS:
		run = False
	if solvePuzzle:
		for _ in range(100):
			if len(board.solveSteps) > 0:
				nextStep = board.solveSteps.pop()
				board.cellArray[nextStep[0]][nextStep[1]].value = nextStep[2]
				board.cellArray[nextStep[0]][nextStep[1]].highlight()
				board.takeNotes()
			else:
				board.clearHighlights()
				solvePuzzle = False
				break
	draw_window(window)

# end of main loop


