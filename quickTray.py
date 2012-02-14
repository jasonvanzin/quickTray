import subprocess
import sys
from functools import partial
from PyQt4 import QtGui, QtCore

class SystemTrayIcon(QtGui.QSystemTrayIcon):
	def __init__(self, menuList, parent=None):
		QtGui.QSystemTrayIcon.__init__(self, parent)

		self.setIcon(QtGui.QIcon("shortcut-icon.png"))

		self.iconMenu = QtGui.QMenu(parent)

		# Submenu object storage
		self.subMenus = []
		# Create menu from menuList variable
		self.add_items_to_menu(menuList, self.iconMenu)
		# Add built-in static entries
		self.iconMenu.addSeparator()
		appabout = self.iconMenu.addAction("About")
		self.connect(appabout,QtCore.SIGNAL('triggered()'),self.showAbout)
		appexit = self.iconMenu.addAction("Exit")
		self.connect(appexit,QtCore.SIGNAL('triggered()'),self.appExit)

		self.setContextMenu(self.iconMenu)

		self.show()

	def add_items_to_menu(self, menuList, Parent):
		for item in menuList:
			if callable(item[1]):
				newItems = Parent.addAction(str(item[0]))
				self.connect(newItems,QtCore.SIGNAL('triggered()'),partial(item[1],self))
			elif non_string_iterable(item[1]):
				self.subMenus.append(QtGui.QMenu(str(item[0])))
				lastIndex = self.subMenus.index(self.subMenus[-1])
				self.add_items_to_menu(item[1], self.subMenus[-1])	# Recursive call for sub-menus
				Parent.addMenu(self.subMenus[lastIndex])
			else:
				newItems = Parent.addAction(str(item[0]))
				self.connect(newItems,QtCore.SIGNAL('triggered()'),partial(self.runCmdStr,str(item[1])))

	def runCmdStr(self, str):
		print str #debug
		args = str.split('|')
		cmd = []
		for arg in args:
			cmd.append(arg)
		subprocess.Popen(cmd)

	def showAbout(self):
		self.iconMenu.setEnabled(False)
		QtGui.QMessageBox.information(QtGui.QMessageBox(), self.tr("About quickTray"), self.tr("quickTray\n\nWritten by Justin Swanson - http://www.h4xful.net/\n\nSource code available at http://www.github.com/geeksunny/quickTray"))
		self.iconMenu.setEnabled(True)
	def appExit(self):
		#sys.exit()
		app.quit()

# Checks the given variable object to see if it is an iterable list or not.
def non_string_iterable(obj):
	try:
		iter(obj)
	except TypeError:
		return False
	else:
		return not isinstance(obj, basestring)

if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	app.setQuitOnLastWindowClosed(False)

	def restartProgram(sysTrayIcon):
		try:
			subprocess.Popen('quickTray.exe')	# Attempts to launch a second instance by calling the executable if it is available.
		except WindowsError:
			try:
				subprocess.Popen('python quickTray.py')	# Assume we are running via python script if the .exe is not available.
			except:
				print "Could not reload program -- sorry!"	# Add better exception handling code here later?
		finally:
			sysTrayIcon.appExit()	# Kill current program

	# Create the menu options list!
	menu_options = []
	try:
		fh = open('shortcuts','r')
		lines = fh.readlines()
		for line in lines:
			line = line.replace("\r\n","")
			line = line.replace("\n","")
			items = line.split(',')
			menu_options.append([str(items[0]), str(items[1])])
		fh.close()
	except IOError as e:
		print "Error! -- " + str(e)
		menu_options = (('Could not load!', 0, 0),)
	# Configuration menu.
	menu_options.append(['Configuration', [['Edit Config', 'notepad|shortcuts'],['Reload Config', restartProgram]]])

	trayIcon = SystemTrayIcon(menu_options)
	trayIcon.show()

	sys.exit(app.exec_())