import sys
import json

def load_json(fileLocation):
    with open(fileLocation) as json_data:
        data_dict = json.load(json_data)
        return data_dict

def indenter(indentLevel):
    text = ""
    for indentCompteur in range(0, indentLevel):
        text += "   "
    return text

def parcours_main(data_dict):
    for key, value in data_dict.items():
        if key == "program":
            for key2, value2 in value.items():
                if key2 == "body":
                    parcours_program(value2, True, 0)

def parcours_program(data_tab, printFlag, indentLevel):
    text = ""
    for value in data_tab:
        text += indenter(indentLevel)
        if value["type"] ==  "ExpressionStatement":
            text += decoder_expression(value["expression"])
            text += ";"
        elif value["type"] == "VariableDeclaration":
            text += decoder_declaration(value["declarations"], value["kind"])
            text += ";"
        elif value["type"] == "WhileStatement":
            text += decoder_whileif(value["test"], value["body"]["body"], indentLevel, "while")
        elif value["type"] == "IfStatement":
            text += decoder_whileif(value["test"], value["consequent"]["body"], indentLevel, "if")
            if value["alternate"] is not None:
                text += decoder_whileif(None, value["alternate"]["body"], indentLevel, " else")
        elif value["type"] == "ForStatement":
            text += decoder_for(value, indentLevel)
        elif value["type"] == "BreakStatement":
            text += "break;"
        elif value["type"] == "ContinueStatement":
            text += "continue;"
        if(printFlag):
            print(text)
            text = ""
        else:
            text += "\n"
    if(printFlag == False):
        return text

def decoder_expression(data_dict):
    if data_dict["type"] == "NumericLiteral" or data_dict["type"] == "BooleanLiteral":
        return str(data_dict["value"])
    elif data_dict["type"] == "BinaryExpression":
        text = "("
        text += decoder_expression(data_dict["left"])
        text += " " + data_dict["operator"] + " "
        text += decoder_expression(data_dict["right"])
        text += ")"
        return text
    elif data_dict["type"] == "Identifier":
        return data_dict["name"]
    elif data_dict["type"] == "UpdateExpression":
        text = decoder_expression(data_dict["argument"])
        text += data_dict["operator"]
        return text
    elif data_dict["type"] == "CallExpression":
        text = decoder_call(data_dict["callee"], data_dict["arguments"])
        return text
    elif data_dict["type"] == "AssignmentExpression":
        text = decoder_expression(data_dict["left"])
        text += data_dict["operator"]
        text += decoder_expression(data_dict["right"])
        return text
    elif data_dict["type"] == "MemberExpression":
        text = decoder_object(data_dict["object"], data_dict["property"])
        return text
    elif data_dict["type"] == "LogicalExpression":
        text = decoder_expression(data_dict["left"])
        text += " " + data_dict["operator"] + " "
        text += decoder_expression(data_dict["right"])
        return text
    return ""

def decoder_declaration(data_tab, kindVar):
    text = kindVar + " "
    notFirstPass = False
    for value in data_tab:
        if(notFirstPass):
            text += ", "
        notFirstPass = True
        idDict = value["id"]
        initDict = value["init"]
        text += idDict["name"]
        if(initDict != None):
            text += " = "
            if(initDict["type"] == "NullLiteral"):
                text += "null"
            elif(initDict["type"] == "StringLiteral"):
                text += "\""
                text += initDict["value"]
                text += "\""
            else:
                text += str(initDict["value"])
    return text

def decoder_whileif(test_dict, data_tab, indentLevel, instruction):
    text = instruction
    text += " "
    if test_dict is None:
        text += "{"
    else:
        text += decoder_expression(test_dict)
        text += " {"
    text += "\n"
    text += parcours_program(data_tab, False, indentLevel + 1)
    text += indenter(indentLevel)
    text += "}"
    return text

def decoder_call(instruction_dict, args_tab):
    text = instruction_dict["name"]
    text += "("
    otherPass = False
    for value in args_tab:
        if otherPass == True:
            text += ","
        text += value["name"]
        otherPass = True
    text += ")"
    return text

def decoder_for(data_dict, indentLevel):
    text = "for ("
    if data_dict["init"] is not None:
        text += decoder_expression(data_dict["init"])
    text += ";"
    text += decoder_expression(data_dict["test"])
    text += ";"
    text += decoder_expression(data_dict["update"])
    text += ")"
    text += " {"
    text += "\n"
    text += parcours_program(data_dict["body"]["body"], False, indentLevel + 1)
    text += indenter(indentLevel)
    text += "}"
    return text

def decoder_object(object_dict, property_dict):
    text = ""
    if object_dict["type"] == "NullLiteral":
        text += "null"
    text += "."
    text += property_dict["name"]
    return text

#Démarrage du décodage
datas = load_json(sys.argv[1])
parcours_main(datas)