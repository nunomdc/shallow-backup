import os
from printing import *
from colorama import Fore
from shutil import copytree, copyfile
from config import get_config
from utils import home_prefix
from utils import run_cmd, get_abs_path_subfiles

# NOTE: Naming convention is like this since the CLI flags would otherwise
#       conflict with the function names.


def reinstall_dots_sb(dots_path):
	"""
	Reinstall all dotfiles and folders by copying them to the home dir.
	"""
	print_section_header("REINSTALLING DOTFILES", Fore.BLUE)
	home_path = os.path.expanduser('~')
	for file in get_abs_path_subfiles(dots_path):
		if os.path.isdir(file):
			copytree(file, home_path, symlinks=True)
		else:
			copyfile(file, home_path)
	print_section_header("DOTFILE REINSTALLATION COMPLETED", Fore.BLUE)
	pass


def reinstall_fonts_sb(fonts_path):
	"""
	Reinstall all fonts.
	TODO: MAKE LINUX/WINDOWS COMPATIBLE.
	"""
	print_section_header("REINSTALLING FONTS", Fore.BLUE)
	# Copy every file in fonts_path to ~/Library/Fonts
	for font in get_abs_path_subfiles(fonts_path):
		home_path = os.path.expanduser('~')
		font_lib_path = os.path.join(home_path, "Library/Fonts")
		dest_path = os.path.join(font_lib_path, font.split("/")[-1])
		copyfile(font, dest_path)
	print_section_header("FONT REINSTALLATION COMPLETED", Fore.BLUE)


def reinstall_configs_sb(configs_path):
	"""
	Reinstall all configs from the backup.
	"""
	print_section_header("REINSTALLING CONFIG FILES", Fore.BLUE)

	def backup_prefix(path):
		return os.path.join(configs_path, path)

	config = get_config()
	configs_dir_mapping = config["config_path_to_dest_map"]
	for target, backup in configs_dir_mapping.items():
		path_to_backup = backup_prefix(backup)
		dest_path = home_prefix(target)
		# TODO: REFACTOR WITH GENERIC COPY FUNCTION.
		if os.path.isdir(path_to_backup):
			copytree(path_to_backup, dest_path)
		elif os.path.isfile(path_to_backup):
			copyfile(path_to_backup, dest_path)

	print_section_header("CONFIG REINSTALLATION COMPLETED", Fore.BLUE)


def reinstall_packages_sb(packages_path):
	"""
	Reinstall all packages from the files in backup/installs.
	"""
	print_section_header("REINSTALLING PACKAGES", Fore.BLUE)

	# Figure out which install lists they have saved
	package_mgrs = set()
	for file in os.listdir(packages_path):
		manager = file.split("_")[0].replace("-", " ")
		if manager in ["gem", "brew-cask", "cargo", "npm", "pip", "brew", "apm", "macports"]:
			package_mgrs.add(file.split("_")[0])

	print_blue_bold("Package Manager Backups Found:")
	for mgr in package_mgrs:
		print_yellow("\t{}".format(mgr))
	print()

	# TODO: Multithreading for reinstallation.
	# construct commands
	for pm in package_mgrs:
		if pm in ["brew", "brew-cask"]:
			pm_formatted = pm.replace("-", " ")
			print_pkg_mgr_reinstall(pm_formatted)
			cmd = "xargs {0} install < {1}/{2}_list.txt".format(pm.replace("-", " "), packages_path, pm_formatted)
			run_cmd(cmd)
		elif pm == "npm":
			print_pkg_mgr_reinstall(pm)
			cmd = "cat {0}/npm_list.txt | xargs npm install -g".format(packages_path)
			run_cmd(cmd)
		elif pm == "pip":
			print_pkg_mgr_reinstall(pm)
			cmd = "pip install -r {0}/pip_list.txt".format(packages_path)
			run_cmd(cmd)
		elif pm == "apm":
			print_pkg_mgr_reinstall(pm)
			cmd = "apm install --packages-file {0}/apm_list.txt".format(packages_path)
			run_cmd(cmd)
		elif pm == "macports":
			print_red_bold("WARNING: Macports reinstallation is not supported.")
		elif pm == "gem":
			print_red_bold("WARNING: Gem reinstallation is not supported.")
		elif pm == "cargo":
			print_red_bold("WARNING: Cargo reinstallation is not possible at the moment."
			                 "\n -> https://github.com/rust-lang/cargo/issues/5593")

	print_section_header("PACKAGE REINSTALLATION COMPLETED", Fore.BLUE)


def reinstall_all_sb(dotfiles_path, packages_path, fonts_path, configs_path):
	"""
	Call all reinstallation methods.
	"""
	reinstall_dots_sb(dotfiles_path)
	reinstall_packages_sb(packages_path)
	reinstall_fonts_sb(fonts_path)
	reinstall_configs_sb(configs_path)
