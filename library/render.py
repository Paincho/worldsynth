#!/usr/bin/env python
"""
Part of the World Generator project. 

author:  Bret Curtis
license: LGPL v2

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
version 2 as published by the Free Software Foundation.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA
02110-1301 USA
"""
from PySide import QtGui
from PySide.QtGui import QImage

if __name__ == '__main__': # handle multiple entry points
    from constants import *
else:
    from .constants import *

class Render():
    '''Transform the numpy data into a renderable image suitable for screen'''

    def __init__( self, world ):
        self.world = world
        for k in self.world:
            exec( 'self.' + k + ' = self.world[k]' )

        self.width, self.height = self.elevation.shape
        self.image = QImage( self.width, self.height, QImage.Format_RGB32 )
        self.image.fill(QtGui.QColor(0,0,0))

    def hex2rgb( self, hexcolor ):
        r = ( hexcolor >> 16 ) & 0xFF;
        g = ( hexcolor >> 8 ) & 0xFF;
        b = hexcolor & 0xFF;
        return [r, g, b]

    def rgb2hex( self, rgb ):
        assert( len( rgb ) == 3 )
        return '#%02x%02x%02x' % rgb

    def convert( self, mapType, seaLevel = None ):
        if seaLevel:
            seaLevel /= 100.0 # reduce to 0.0 to 1.0 range
            
        background = []
        if mapType == "heightmap":
            heightmap = self.elevation * 255 # convert to greyscale
            for x in range( self.width ):
                for y in range( self.height ):
                    gValue = heightmap[x, y]
                    self.image.setPixel( x, y, QtGui.QColor( gValue, gValue, gValue ).rgb() )

        elif mapType == "sealevel":
            for x in range( self.width ):
                for y in range( self.height ):
                    elevation = self.elevation[x, y]
                    gValue = elevation * 255
                    if elevation <= seaLevel:
                        self.image.setPixel( x, y, QtGui.QColor( 0, 0, gValue ).rgb() )
                    else:
                        self.image.setPixel( x, y, QtGui.QColor( gValue, gValue, gValue ).rgb() )

        elif mapType == "elevation":
            for x in range( self.width ):
                for y in range( self.height ):
                    elevation = self.elevation[x, y]
                    if elevation <= seaLevel:
                        if elevation < seaLevel/4.0:
                            self.image.setPixel( x, y, COLOR_DEEPSEA )
                        elif elevation < seaLevel/2.0:
                            self.image.setPixel( x, y, COLOR_SEA )
                        else:
                            self.image.setPixel( x, y, COLOR_BLUE )
                    else:
                        if elevation < 0.65:
                            self.image.setPixel( x, y, COLOR_GRASSLAND )
                        elif elevation < 0.95:
                            self.image.setPixel( x, y, COLOR_HILLS )
                        else:
                            self.image.setPixel( x, y, COLOR_WHITE )

        elif mapType == "heatmap":
            for x in range( self.width ):
                for y in range( self.height ):
                    gValue = self.temperature[x, y]
                    self.image.setPixel( x, y, QtGui.QColor( gValue * 255, gValue * 128, ( 1 - gValue ) * 255 ).rgb() )

        elif mapType == "rawheatmap":
            temperature = self.temperature * 255 # convert to greyscale
            for x in range( self.width ):
                for y in range( self.height ):
                    gValue = temperature[x, y]
                    self.image.setPixel( x, y, QtGui.QColor( gValue, gValue, gValue ).rgb() )

        elif mapType == 'windmap':
            for x in range( self.width ):
                for y in range( self.height ):
                    gValue = self.wind[x, y]
                    self.image.setPixel( x, y, QtGui.QColor( 0, gValue * 255, 0 ).rgb() )

        elif mapType == 'rainmap':
            for x in range( self.width ):
                for y in range( self.height ):
                    gValue = self.rainfall[x, y]
                    self.image.setPixel( x, y, QtGui.QColor( gValue * 100, gValue * 100, gValue * 255 ).rgb() )

        elif mapType == 'windandrainmap':
            for x in range( self.width ):
                for y in range( self.height ):
                    rain = int( 255 * min( self.wind[x, y], 1.0 ) )
                    wind = int( 255 * min( self.rainfall[x, y], 1.0 ) )
                    self.image.setPixel( x, y, QtGui.QColor( 0, wind, rain ).rgb() )

        elif mapType == 'drainagemap':
            drainage = self.drainage * 255 # convert to greyscale
            for x in range( self.width ):
                for y in range( self.height ):
                    gValue = drainage[x, y]
                    self.image.setPixel( x, y, QtGui.QColor( gValue, gValue, gValue ).rgb() )

        elif mapType == 'rivermap':
            for x in range( self.width ):
                for y in range( self.height ):
                    gValue = self.elevation[x, y] * 255
                    if self.elevation[x, y] <= seaLevel: 
                        self.image.setPixel( x, y, QtGui.QColor( 0, 0, gValue ).rgb() )
                    else:
                        rgb = QtGui.QColor( gValue, gValue, gValue ).rgb()
                        if self.rivers[x, y] > 0.0:
                            rgb = COLOR_COBALT
                        if self.lakes[x, y] > 0.0:
                            rgb = COLOR_AZURE
                        self.image.setPixel( x, y, rgb )

        elif mapType == 'biomemap':
            for x in range( self.width ):
                for y in range( self.height ):
                    self.image.setPixel( x, y, self.biomeColour[x, y] )

        elif mapType == "erosionmap":
            erosion = self.erosion * 255 # convert to greyscale
            for x in range( self.width ):
                for y in range( self.height ):
                    gValue = erosion[x, y] 
                    self.image.setPixel( x, y, QtGui.QColor( gValue, gValue, gValue ).rgb() )

        elif mapType == "erosionappliedmap":
            erosion = ( self.elevation - self.erosion ) *  255 # convert to greyscale
            for x in range( self.width ):
                for y in range( self.height ):
                    gValue = erosion[x, y]
                    self.image.setPixel( x, y, QtGui.QColor( gValue, gValue, gValue ).rgb() )

        else: # something bad happened...
            print("did not get a valid map type, check your bindings programmer man!")
            print(len( background ), background, mapType)
            from numpy import zeros
            background = zeros( ( self.width, self.height ), dtype = "int32" )

        return self.image
