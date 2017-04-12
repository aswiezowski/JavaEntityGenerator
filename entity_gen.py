import argparse
import re
from functools import reduce

# Usage: python ./entity_gen.py --equals --toString --hashCode --get --set --builder --class ClassName propertyType:propertyName ...

parser = argparse.ArgumentParser(description='Generate class with properties')
parser.add_argument('properties', metavar='Type:Name', nargs='+',
                    help='properties to be used')
parser.add_argument('--class', dest="className", default="Entity")
parser.add_argument('--equals', action='store_true')
parser.add_argument('--toString', action='store_true')
parser.add_argument('--hashCode', action='store_true')
parser.add_argument('--get', action='store_true')
parser.add_argument('--set', action='store_true')
parser.add_argument('--builder', action='store_true')

args = parser.parse_args()


def createEntity(args):
    buildedString = ""
    buildedString += getImports()
    buildedString += "\n"
    buildedString += getClassDefinition(args.className)
    buildedString += "\n"
    buildedString += getPropertiesDefinition(args.properties, not args.set)
    buildedString += "\n"

    if args.get:
        buildedString += getGetFunctions(args.properties)

    if args.set:
        buildedString += getSetFunctions(args.properties)

    if args.equals:
        buildedString += getEquals(args.className, args.properties)
        buildedString += "\n"

    if args.hashCode:
        buildedString += getHashCode(args.properties)
        buildedString += "\n"

    if args.toString:
        buildedString += getToString(args.properties)
        buildedString += "\n"

    if args.builder:
        buildedString += getBuilder(args.className, args.properties)
        buildedString += "\n"

    buildedString += getClassClose()
    return buildedString


def getType(arg):
    return arg.split(":")[0]


def getName(arg):
    return arg.split(":")[1]


def indent(num):
    return " " * 4 * num


def getImports():
    return """import java.util.Objects;
import com.google.common.base.MoreObjects;"""


def getClassDefinition(className):
    return "public final class " + className + "{"


def getPropertiesDefinition(properites, isFinal):
    str = ""
    finalModifier = ""
    if isFinal:
        finalModifier = "final "
    for prop in properites:
        str += indent(1) + "private " + finalModifier + getType(prop) + " " + getName(prop) + ";\n"
    return str


def getGetFunctions(properites):
    str = ""
    for prop in args.properties:
        str += indent(1) + "public final " + getType(prop) + " get" + formatVariableName(
            prop) + "(){\n" + "        return " + getName(prop) + ";\n" + indent(1) + "}\n\n"
    return str


def getSetFunctions(properties):
    str = ""
    for prop in properties:
        str += indent(1) + "public final void set" + formatVariableName(prop) + "(" + getType(
            prop) + " p" + formatVariableName(prop) + "){\n" + indent(2) + getName(prop) + " = p" + formatVariableName(
            prop) + ";\n" + indent(1) + "}\n\n"
    return str


def formatVariableName(name):
    return getName(name)[0].upper() + getName(name)[1:]


def getEquals(className, properties):
    objName = className.lower()
    str = indent(1) + """@Override
    public boolean equals(Object object){
        if(object == this){
            return true;
        }\n"""
    str += indent(2) + "if(object instanceof " + args.className + "){\n" + indent(
        3) + args.className + " " + objName + " = (" + args.className + ") object;\n"
    str += indent(3) + "if(" + reduce(lambda x, y: x + " && " + y, map(
        lambda prop: "Objects.equals(" + getName(prop) + ", " + objName + "." + getName(prop) + ")",
        properties)) + ") {\n"
    str += """                return true;
            }
        }
        return false;
    }"""
    return str


def getHashCode(properties):
    str = indent(1) + """@Override
    public int hashCode(){\n"""
    str += indent(2) + "return Objects.hash(" + reduce(lambda x, y: x + ", " + y,
                                                       map(lambda x: getName(x), properties)) + ");\n" + indent(1) + "}"
    return str


def getToString(properties):
    str = indent(1) + """@Override
    public String toString(){\n"""
    str += indent(2) + "return MoreObjects.toStringHelper(this)" + ''.join(
        map(lambda x: "\n" + indent(3) + ".add(\"" + x + "\", " + x + ")",
            map(lambda x: getName(x), properties))) + ".toString();\n" + "    }"
    return str


def getBuilder(className, properties):
    str = getConstructorForBuilder(className, properties)
    str += "\n"

    str += getBuilderCreator()
    str += "\n"

    str += indent(1) + "public static class Builder{\n\n"
    str += getPropertiesForBuilder(properties);
    str += "\n"

    str += getSettersForBuilder(properties)

    str += getBuilderExecutor()
    str += "\n"

    str += indent(1) + "}\n"
    return str


def getConstructorForBuilder(className, properties):
    str = indent(1) + "private " + className + "(Builder pBuilder){\n"
    for prop in properties:
        str += indent(2) + getName(prop) + " = pBuilder." + getName(prop) + ";\n"
    return str + indent(1) + "}\n"


def getBuilderCreator():
    return indent(1) + """public static Builder builder(){
        return new Builder();
    }\n"""


def getPropertiesForBuilder(properties):
    str = ""
    for prop in properties:
        propertyType = getType(prop)
        str += indent(2) + "private " + propertyType + " " + getName(prop) + getInitialization(propertyType) + ";\n"
    return str


def getInitialization(propertyType):
    match = re.search("^([^<]*)<([^>]*)>", propertyType)
    if match:
        return " = " + getDefaultInitialization(match.group(1))
    else:
        return ""


def getDefaultInitialization(genericType):
    if genericType == "Optional":
        return "Optional.empty()"
    if genericType == "Set":
        return "new HashSet<>()"
    if genericType == "List":
        return "new ArrayList<>()"
    if genericType == "Map":
        return "new HashMap<>()"
    return "new " + genericType + "<>()"


def getSettersForBuilder(properties):
    str = ""
    for prop in properties:
        str += indent(2) + "public Builder " + getName(prop) + "(" + getType(prop) + " p" + formatVariableName(
            prop) + "){\n"
        str += indent(3) + getName(prop) + " = p" + formatVariableName(prop) + ";\n"
        str += indent(3) + "return this;\n"
        str += indent(2) + "}\n\n"
    return str


def getBuilderExecutor():
    str = indent(2) + "public " + args.className + " build(){\n"
    str += indent(3) + "return new " + args.className + "(this);\n" + indent(2)
    return str + "}"


def getClassClose():
    return "}"


print(createEntity(args))
