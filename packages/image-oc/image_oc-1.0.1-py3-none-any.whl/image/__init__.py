# coding=utf8
"""Image

Module to manipulate images and photos, requires the Python Pillow library
"""

__author__		= "Chris Nasr"
__copyright__	= "Ouroboros Coding Inc."
__version__		= "1.0.0"
__email__		= "chris@ouroboroscoding.com"
__created__		= "2024-12-26"

# Limit exports
__all__ = [
	'apply_rotation', 'convert_to_jpeg', 'crop', 'info', 'Info', 'resize',
	'Resolution', 'WEB_MIME_TO_EXT', 'WEB_MIMES', 'XY'
]

# Ouroboros imports
from tools import crop as crop_tool, fit as fit_tool
import undefined

# Python imports
from io import BytesIO
from typing import Literal, TypedDict

# Pip Imports
import piexif
from PIL import Image as Pillow, ImageFile as PillowFile
PillowFile.LOAD_TRUNCATED_IMAGES = True

_ORIENTATION_TAG = 0x0112
"""exif rotation tag"""

_SEQUENCES = [
	[],
	[Pillow.FLIP_LEFT_RIGHT],
	[Pillow.ROTATE_180],
	[Pillow.FLIP_TOP_BOTTOM],
	[Pillow.FLIP_LEFT_RIGHT, Pillow.ROTATE_90],
	[Pillow.ROTATE_270],
	[Pillow.FLIP_TOP_BOTTOM, Pillow.ROTATE_90],
	[Pillow.ROTATE_90]
]
"""Rotation sequences based on exif orientation flag"""

WEB_MIME_TO_EXT = {
	'image/jpeg': '.jpg',
	'image/png': '.png',
	'image/webp': '.webp'
}
"""Mapping of valid image mimes to extentions"""

WEB_MIMES = [
	'image/jpeg',
	'image/png',
	'image/webp'
]
"""List of valid web image mime types"""

class Info(TypedDict):
	"""Info method return structure"""
	exif: dict | None
	height: int
	length: int
	mime: str
	orientation: int | Literal[False]
	type: str
	width: int

class XY(TypedDict):
	"""Holds xy (pixel) data points"""
	x: int
	y: int

class Resolution(TypedDict):
	"""Holds resolution (pixel) data points"""
	height: int
	width: int

def apply_rotation(image: str) -> str:
	"""Apply Rotation

	Uses exif data to rotate the image to the proper position, will lose exif
	data and might lose quality

	Arguments:
		image (str): A raw image as a string

	Returns:
		str
	"""

	# Load the image into a new BytesIO
	sImg = BytesIO(image)
	sNewImg = BytesIO(b'')

	# Create a new Pillow instance from the raw data
	oImg = Pillow.open(sImg)

	# Store the image format
	sFormat = oImg.format

	# Get the proper sequence
	try:
		lSeq = _SEQUENCES[oImg._getexif()[_ORIENTATION_TAG] - 1]

		# Transpose the image
		for i in lSeq:
			oImg = oImg.transpose(i)

		# Save the image using the same format as we got it in
		oImg.save(sNewImg, sFormat)

		# Get the raw bytes
		sRet = sNewImg.getvalue()

	# If there's no sequence, return the image as is
	except Exception as e:
		sRet = image

	# Cleanup
	oImg.close()
	sImg.close()
	sNewImg.close()

	# Return
	return sRet

def convert_to_jpeg(image: str, quality: int = 90) -> str:
	"""Convert To JPEG

	Changes any valid image into a JPEG, loses exif data

	Arguments:
		image (str): A raw image as a string
		quality (uint): The quality, from 0 to 100, to save the image in

	Returns:
		str
	"""

	# Load the image into a new BytesIO
	sImg = BytesIO(image)

	# Create an empty BytesIO for the new image
	sNewImg = BytesIO(b'')

	# Create a new Pillow instance from the raw data
	oImg = Pillow.open(sImg)

	# If the mode is not valid
	if oImg.mode not in ('1','L','RGB','RGBA'):
		oImg = oImg.convert('RGB')

	# Save the new image as a JPEG
	oImg.save(sNewImg, 'JPEG', quality=quality, subsampling=0)

	# Pull out the raw string
	sRet = sNewImg.getvalue()

	# Close the image
	oImg.close()

	# Return the new image
	return sRet

def crop(
	image: str,
	start: XY,
	size: Resolution,
	quality: int = 90,
	format: str = undefined
) -> str:
	"""Crop

	Given raw data, a starting point, and dimensions, a new image is created
	and returned as raw data

	Arguments:
		image (str): Raw image data to be loaded and cropped
		start (XY): The x and y points to start from
		size (Resolution): The width and height of the new image
		quality (uint): The quality, from 0 to 100, to save the thumbnail in
		format (str): The optional format to use instead of the original

	Returns:
		str
	"""

	# Load the image into a new BytesIO
	sImg = BytesIO(image)
	sNewImg = BytesIO(b'')

	# Create a new Pillow instance from the raw data
	oImg = Pillow.open(sImg)

	# Store the format
	sFormat = format or oImg.format

	# If the image has an orientation
	try:
		lSeq = _SEQUENCES[oImg._getexif()[_ORIENTATION_TAG] - 1]

		# Transpose the image
		for i in lSeq:
			oImg = oImg.transpose(i)
	except Exception:
		pass

	# Crop the image
	oImgCrop = oImg.crop((
		start['x'], start['y'],
		start['x'] + size['width'], start['y'] + size['height']
	))

	# Save the new image to a BytesIO
	oImgCrop.save(sNewImg, sFormat, quality = quality, subsampling = 0)

	# Pull out the raw string
	sReturn = sNewImg.getvalue()

	# Cleanup
	oImgCrop.close()
	oImg.close()
	sImg.close()

	# Return the new string
	return sReturn

def info(image: str) -> Info:
	"""Info

	Returns information about an image: resolution, length, type, and mime

	Arguments:
		image (str): A raw image as a string

	Returns:
		Info
	"""

	# Load the image into a new BytesIO
	sImg = BytesIO(image)

	# Create a new Pillow instance from the raw data
	oImg = Pillow.open(sImg)

	# Get the details
	dInfo = {
		'height': oImg.size[1],
		'length': len(image),
		'mime': oImg.format in Pillow.MIME and Pillow.MIME[oImg.format] or None,
		'type': oImg.format,
		'width': oImg.size[0]
	}

	# Check for exif rotation data
	try:
		dInfo['orientation'] = oImg._getexif()[_ORIENTATION_TAG]
	except Exception:
		dInfo['orientation'] = False

	# Check for exif data
	try:
		dInfo['exif'] = piexif.load(oImg.info['exif'])
	except Exception:
		dInfo['exif'] = None

	# Cleanup
	sImg.close()
	oImg.close()

	# Return the info
	return dInfo

def resize(
	image: str,
	size: Resolution,
	crop: bool = False,
	quality: int = 90,
	format: str = undefined
) -> str:
	"""Resize

	Given raw data and dimensions, a new image is created and returned as raw
	data

	Arguments:
		image (str): Raw image data to be loaded and resized
		size (str|dict): New dimensions of the image, "WWWxHHH" or {"w":, "h":}
		crop (bool): Set to true to crop the photo rather than add whitespace
		quality (uint): The quality, from 0 to 100, to save the thumbnail in
		format (str): The optional format to use instead of the original

	Returns:
		str
	"""

	# Load the image into a new BytesIO
	sImg = BytesIO(image)
	sNewImg = BytesIO(b'')

	# Create a new Pillow instance from the raw data
	oImg = Pillow.open(sImg)

	# Store the format
	sFormat = format or oImg.format

	# Create a new blank image
	oNewImg = Pillow.new(
		oImg.mode,
		[ size['width'], size['height'] ],
		(oImg.mode in [ '1', 'L', 'LA' ] and 255 \
			or ( 255, 255, 255, 255 ))
	)

	# If the image has an orientation
	try:
		lSeq = _SEQUENCES[oImg._getexif()[_ORIENTATION_TAG] - 1]

		# Transpose the image
		for i in lSeq:
			oImg = oImg.transpose(i)
	except Exception:
		pass

	# If we are cropping
	if crop:
		dResize = crop_tool(oImg.width, oImg.height, size['width'], size['height'])

	# Else, we are fitting
	else:
		dResize = fit_tool(oImg.width, oImg.height, size['width'], size['height'])

	# Resize the image
	oImg.thumbnail([ dResize['w'], dResize['h'] ], Pillow.LANCZOS)

	# Get the offsets
	lOffset = (
		(size['width'] - dResize['w']) // 2,
		(size['height'] - dResize['h']) // 2
	)

	# Paste the resized image onto the new canvas
	oNewImg.paste(oImg, lOffset)

	# Save the new image to a BytesIO
	oNewImg.save(sNewImg, sFormat, quality = quality, subsampling = 0)

	# Pull out the raw string
	sReturn = sNewImg.getvalue()

	# Cleanup
	oNewImg.close()
	oImg.close()
	sImg.close()

	# Return the new string
	return sReturn