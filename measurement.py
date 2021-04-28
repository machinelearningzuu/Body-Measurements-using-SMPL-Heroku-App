import numpy as np
import trimesh
import math

def getMinX(polygon):
    return polygon.bounds[0]

def getMinY(polygon):
    return polygon.bounds[1]

def getMaxX(polygon):
    return polygon.bounds[2]

def getMaxY(polygon):
    return polygon.bounds[3]

def getArmpits(sections):
    location_percentage = 76 # percentage
    approximate_location = math.floor(location_percentage*len(sections)/100)
    section_min = approximate_location - 10
    section_max = approximate_location + 10
    range_sections = range(section_min, section_max)
    armpits = None
    position = None
    length = None
    stop = False
    for index in range_sections:
        if stop == False:
            if len(sections[index].entities) == 1:
                armpits = sections[index]
                position = index
                length = sections[index].polygons_closed[0].length
                stop = True
                
    return armpits, position, length

def getChest (sections, armpits_location):
    cont = armpits_location
    stop = False
    minimum = 100
    chest = None
    position = None
    length = None
    while stop == False:
        polygon = getLargerAreaPolygon(sections[cont])
        minimumPolygonX = getMinX(polygon)
        if minimumPolygonX < minimum:
            minimum = minimumPolygonX
            chest = sections[cont]
            position = cont
            length = polygon.length
        else:
            stop = True
        cont = cont - 1
        
    return chest, position, length

def getCrotch(sections):
    location_percentage = 47 # percentage
    approximate_location = math.floor(location_percentage*len(sections)/100)
    section_min = approximate_location - 15
    section_max = approximate_location + 15
    range_sections = range(section_min, section_max)
    
    crotch = None
    position = None
    length = None
    stop = False
    for index in range_sections:
        if stop == False:
            if len(sections[index].entities) == 1:
                crotch = sections[index]
                position = index
                length = sections[index].polygons_closed[0].length
                stop = True
                
    return crotch, position, length

def getWaist(sections, hip_location):
    cont = hip_location
    stop = False
    minimum = 999
    waist = None
    position = None
    length = None
    while stop == False:
        polygon = getLargerAreaPolygon(sections[cont])
        maximumPolygonX = getMaxX(polygon)
        if maximumPolygonX < minimum:
            minimum = maximumPolygonX
            waist = sections[cont]
            position = cont
            length = polygon.length
        else:
            stop = True
        cont = cont + 1
        
    return waist, position, length

def getSections(mesh, levels):
    sections = mesh.section_multiplane(plane_origin=mesh.centroid,
                                   plane_normal=[0,1,0], 
                                   heights=levels)
    new_sections = []
    cont = 0
    for item in sections:
        if item != None:
            new_sections.append(item)
            cont = cont + 1
    return new_sections
                                
def getLargerAreaPolygon(section):
    higher = 0
    polygon = None
    for pol in section.polygons_closed:
        if pol != None:
            if pol.area > higher:
                higher = pol.area
                polygon = pol
    return polygon

def getHeight(mesh):
    slice_r = mesh.section(plane_origin=mesh.centroid, 
                     plane_normal=[0,0,1])
    slice_2D, _ = slice_r.to_planar()
    minY = slice_2D.bounds[0][1]
    maxY = slice_2D.bounds[1][1]
    return (maxY - minY) # meters

def getHip(sections, crotch_location):
    cont = crotch_location
    stop = False
    maximum = 0
    hip = None
    position = None
    length = None
    while stop == False:
        polygon = getLargerAreaPolygon(sections[cont])
        maximumPolygonX = getMaxX(polygon)
        if maximumPolygonX > maximum:
            maximum = maximumPolygonX
            hip = sections[cont]
            position = cont
            length = polygon.length
        else:
            stop = True
        cont = cont + 1
        
    return hip, position, length

class Body3D(object):
    def __init__(self, vertices, faces, steps=0.005, levels=[-1.5, 1.5]):
        self.vertices = vertices
        self.faces = faces
        self.steps = steps
        self.levels = np.arange(levels[0], levels[1], step=self.steps)
        self.mesh = trimesh.Trimesh(self.vertices, self.faces)
        self.sections = getSections(self.mesh, self.levels)

        self.armpits_location = getArmpits(self.sections)[1]
        self.crotch_location = getCrotch(self.sections)[1]
        self.hip_location = getHip(self.sections, self.crotch_location)[1]

    def getMeasurements(self):
        height = getHeight(self.mesh)
        chest_length = getChest(self.sections, self.armpits_location)[2]
        waist_length = getWaist(self.sections, self.hip_location)[2]

        return height, chest_length, waist_length

    def height(self):
        return getHeight(self.mesh)

    def chest(self):
        return getChest(self.sections, self.armpits_location)

    def waist(self):
        return getWaist(self.sections, self.hip_location)