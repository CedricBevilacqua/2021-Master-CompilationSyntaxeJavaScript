import sys
import json

#Stockage des données
variables = dict() #Stockage des valeurs des variables
kindVariables = dict() #Stockage du type des variables (var ou const, const n'est pas encore implémenté)
askChange = dict() #Répertorie toutes les instructions qui ont été appelées et doivent être pris en  compte dans la  pile d'exécution
askChange["break"] = False #Activation du break lors de l'appel de l'instruction pour qu'elle soit répercutée sur la pile d'exécution
askChange["continue"] = False  #Activation du continue lors de l'appel de l'instruction pour qu'elle soit répercutée sur la pile d'exécution
askChange["return"]  = (False,None)
functionName = [] #Nom des fonctions dans l'ordre où elles ont été chargées (l'index est important)
functionData = [] #Contenu des fonctions dans l'ordre où elles ont été chargées afin de pouvoir les exécuter
functionParam = [] #Nom des paramètres des fonctions dans l'ordre où elles ont été chargées afin de pouvoir donner un nom aux arguments
functionVar = [] #Liste de dictionnaires des variables pour chaque fonction en cours d'exécution
execPile = []
classMemory = dict()
instanceMemory = dict()

class jsObject:
    def __init__(self):
        self.set_attributs(dict())
        self.set_methodes(dict())

    def get_attributs(self):
        return self.attributs

    def set_attributs(self, attributs):
        self.attributs = attributs

    def get_methodes(self):
        return self.methodes

    def set_methodes(self, methodes):
        self.methodes = methodes


def load_json(fileLocation):
    """
        Chargement de la structure json sous format dictionnaire
        : param (File): fileLocation fichier contenant la structure json
        : return (dict) dictionnaire
    """
    with open(fileLocation) as json_data:
        data_dict = json.load(json_data)
        return data_dict


def indenter(indentLevel):
    """
        Ajoute un espace vide selon le nombre d'intentation voulue
        : param indeLevel (int): le nombre de fois que l'on veut indenter
        : return (str) chaine de caractere
    """
    text = ""
    for indentCompteur in range(0, indentLevel):
        text += "   "
    return text

def parcours_main(data_dict):
    """
        parcours la partie body de l'arbre syntaxique
        : param data_dict (dict): le dictionnaire que l'on veut parser
        : return (str) l'execution de l'expression
    """
    for key, value in data_dict.items():
        if key == "program":
            for key2, value2 in value.items():
                if key2 == "body":
                    parcours_program(value2, 0, True)

def parcours_program(data_tab, indentLevel, printFlag):
    """
        decode chaque instruction selon son type assigné et affiche le resultat
        : param data_tab (dict): le dictionnaire que l'on veut parser
        : param indentLevel (int): niveau d'intentation demandée
        : param printFlag (Bool): affiche si c'est à True sinon cela va faire un return
        : return (str) l'execution de l'expression
    """
    text = ""
    for value in data_tab:
        if(askChange["continue"] or askChange["break"]):
            return text
        text += indenter(indentLevel)
        if value["type"] == "ExpressionStatement":
            text += str(decoder_expression(value["expression"]))
        elif value["type"] == "VariableDeclaration":
            text += decoder_declaration(value["declarations"], value["kind"])
        elif value["type"] == "WhileStatement":
            text += decoder_whileif(value["test"], value["body"]["body"], indentLevel, "while")
        elif value["type"] == "IfStatement":
            text += decoder_whileif(value["test"], value["consequent"]["body"], indentLevel, "if")
            if value["alternate"] is not None:
                text += "\n"
                text += decoder_whileif(value["test"], value["alternate"]["body"], indentLevel, "else")
        elif value["type"] == "ForStatement":
            text += decoder_for(value, indentLevel)
        elif value["type"] == "BreakStatement":
            text += "Instruction break\n"
            askChange["break"] = True
            return text
        elif value["type"] == "ContinueStatement":
            text += "Instruction continue"
            askChange["continue"] = True
            return text
        elif value["type"] == "FunctionDeclaration":
            functionName.append(value["id"]["name"])
            functionData.append(value["body"]["body"])
            functionVar.append(dict())
            paramTab = []
            for param in value["params"]:
                paramTab.append(param["name"])
            functionParam.append(paramTab)
            text += "Fonction " + value["id"]["name"] + " chargée"
        elif value["type"] == "ReturnStatement":
            if(value["argument"] != None):
                askChange["return"] = (True,decoder_expression(value["argument"]))
            else:
                askChange["return"] = (True,None)
            if(printFlag == True):
                print(text)
            return text
        elif value["type"] == "ClassDeclaration":
            text += "Déclaration de la classe " + value["id"]["name"]
            classMemory[value["id"]["name"]] = value["body"]["body"]
        if(printFlag):
            print(text)
            text = ""
        else:
            text += "\n"
    if(printFlag == False):
        return text

def decoder_expression(data_dict):
    """
        decode chaque expression 
        : param data_dict (dict): le dictionnaire que l'on veut parser
        : return (str) 
    """
    if data_dict["type"] == "NumericLiteral" or data_dict["type"] == "BooleanLiteral":
        return int(data_dict["value"])
    elif data_dict["type"] == "BinaryExpression":
        calculLeft  = decoder_expression(data_dict["left"])
        calculRight = decoder_expression(data_dict["right"])
        if(calculRight!=None and calculLeft!=None):
            if(data_dict["operator"] == "+"):
                return calculLeft + calculRight
            elif(data_dict["operator"] == "-"):
                return calculLeft - calculRight
            elif(data_dict["operator"] == "*"):
                return calculLeft * calculRight
            elif(data_dict["operator"] == "/"):
                return calculLeft / calculRight
            elif(data_dict["operator"] == "<"):
                return calculLeft < calculRight
            elif(data_dict["operator"] == "<="):
                return calculLeft >= calculRight
            elif(data_dict["operator"] == ">"):
                return calculLeft > calculRight
            elif(data_dict["operator"] == ">="):
                return calculLeft >= calculRight
            elif(data_dict["operator"] == "=="):
                return calculLeft == calculRight
            elif(data_dict["operator"] == "!="):
                return calculLeft != calculRight
        else:
            print("Erreur l'une des variables est indéfini")
    elif data_dict["type"] == "Identifier":
        if len(execPile) > 0:
            execVal = execPile[len(execPile)-1]
            if data_dict["name"] in functionVar[execVal].keys():
                return functionVar[execVal][data_dict["name"]]
        return variables[data_dict["name"]]
    elif data_dict["type"] == "UpdateExpression":
        if(data_dict["operator"] == "++"):
            if len(execPile) > 0 and data_dict["argument"]["name"] in functionVar[execPile[len(execPile)-1]].keys():
                functionVar[execPile[len(execPile)-1]][data_dict["argument"]["name"]] = functionVar[execPile[len(execPile)-1]][data_dict["argument"]["name"]] + 1
            else:
                variables[data_dict["argument"]["name"]] = variables[data_dict["argument"]["name"]] + 1
        text = "UpdateExpression: "
        text += data_dict["argument"]["name"]
        text += data_dict["operator"]
        return text
    elif data_dict["type"] == "CallExpression":
        text = str(decoder_call(data_dict["callee"], data_dict["arguments"]))
        return text
    elif data_dict["type"] == "AssignmentExpression":
        text = ""
        if(data_dict["operator"] == "="):
            if len(execPile) > 0 and data_dict["left"]["name"] in functionVar[execPile[len(execPile)-1]].keys():
                functionVar[execPile[len(execPile)-1]][data_dict["left"]["name"]] = decoder_expression(data_dict["right"])
            else:
                variables[data_dict["left"]["name"]] = decoder_expression(data_dict["right"])
        elif(data_dict["operator"] == "+="):
            if len(execPile) > 0 and data_dict["left"]["name"] in functionVar[execPile[len(execPile)-1]].keys():
                functionVar[execPile[len(execPile)-1]][data_dict["left"]["name"]] = functionVar[execPile[len(execPile)-1]][data_dict["left"]["name"]] + decoder_expression(data_dict["right"])
            else:
                variables[data_dict["left"]["name"]] = variables[data_dict["left"]["name"]] + decoder_expression(data_dict["right"])
        elif(data_dict["operator"] == "-="):
            if len(execPile) > 0 and data_dict["left"]["name"] in functionVar[execPile[len(execPile)-1]].keys():
                functionVar[execPile[len(execPile)-1]][data_dict["left"]["name"]] = functionVar[execPile[len(execPile)-1]][data_dict["left"]["name"]] - decoder_expression(data_dict["right"])
            else:
                variables[data_dict["left"]["name"]] = variables[data_dict["left"]["name"]] - decoder_expression(data_dict["right"])
        text += "AssignmentExpression: "
        text += data_dict["left"]["name"]
        text += data_dict["operator"]
        text += str(decoder_expression(data_dict["right"]))
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
    """
       Déclare une  variable
        : param data_tab (dict): le dictionnaire que l'on veut parser
        : param kindVar (dict): le type de variable
        : return (str) 
    """
    notFirstPass = False
    text = ""
    for value in data_tab:
        if(notFirstPass):
            text += "\n"
        notFirstPass = True
        text += "VariableDeclaration: "
        kindVariables[value["id"]["name"]] = kindVar
        if(value["init"] != None):
            if(value["init"]["type"] == "NewExpression"):
                print("OH")
                instanceMemory[value["callee"]["name"]] = jsObject()
            elif(value["init"]["type"] != "NullLiteral"):
                text += value["id"]["name"] + " " + str(value["init"]["value"])
                if len(execPile) > 0:
                    functionVar[execPile[len(execPile)-1]][value["id"]["name"]] = value["init"]['value']
                else:
                    variables[value["id"]["name"]] = value["init"]['value']
            else:
                text += value["id"]["name"] + " " + "null"
                if len(execPile) > 0:
                    functionVar[execPile[len(execPile)-1]][value["id"]["name"]] = None
                else:
                    variables[value["id"]["name"]] = None
        else:
            text += value["id"]["name"]
            if len(execPile) > 0:
                functionVar[execPile[len(execPile)-1]][value["id"]["name"]] = None
            else:
                variables[value["id"]["name"]] = None
    return text

def decoder_whileif(test_dict, data_tab, indentLevel, instruction):
    """
        applique une boucle 
        : param test_dict (dict): la condition de la boucle
        : param data_tab (dict): le corps de la boucle
        : param indentLevel (int): le nombre d 'indentation à ajouter
        : param instruction (str): le type d'instruction de boucle
        : return (str) 
    """
    if(instruction == "while"):
        while(decoder_expression(test_dict) and askChange["break"] == False):
            parcours_program(data_tab, indentLevel + 1, True)
            if(askChange["continue"] == True):
                askChange["continue"] = False
        if(askChange["break"] == True):
            askChange["break"] = False
        return "Fin de la boucle while"
    elif(instruction == "if"):
        if(decoder_expression(test_dict)):
            parcours_program(data_tab, indentLevel + 1, True)
        return "Fin de la condition if"
    elif(instruction == "else"):
        if(decoder_expression(test_dict) == False):
            parcours_program(data_tab, indentLevel + 1, True)
        return "Fin de la condition else"
    return ""

def decoder_call(instruction_dict, args_tab):
    text = ""
    if(instruction_dict["name"] == "print"):
        text += str(decoder_expression(args_tab[0]))
    else:
        for funcName in range(0, len(functionName)):
            if(functionName[funcName] == instruction_dict["name"]):
                compteurBoucle = 0
                for arg in args_tab:
                    if arg["type"] == "NumericLiteral" or arg["type"] == "BooleanLiteral":
                        functionVar[funcName][functionParam[funcName][compteurBoucle]] = arg["value"]
                    compteurBoucle = compteurBoucle + 1
                execPile.append(funcName)
                parcours_program(functionData[funcName], 0, True)
                returnedValue = askChange["return"][1]
                askChange["return"] = (False,None)
                execPile.pop()
                functionVar[funcName].clear()
                return returnedValue
    return text

def decoder_for(data_dict, indentLevel):
    """
        applique une boucle 
        : param data_dict (dict): la boucle for et son contenu
        : param indentLevel (int): le niveau d'indentation a ajouter dans l'expression final
        : return (str) 
    """
    text = "Début boucle for\n"
    if data_dict["init"] is not None:
        text += decoder_expression(data_dict["init"])
        text += "\n"
    while(decoder_expression(data_dict["test"]) and askChange["break"] == False):
        if(askChange["break"] == True):
            break
        text += decoder_expression(data_dict["update"])
        text += "\n"
        text += parcours_program(data_dict["body"]["body"], indentLevel + 1, False)
        if(askChange["continue"] == True):
            askChange["continue"] = False
    text += "Fin boucle for"
    if(askChange["break"] == True):
        askChange["break"] = False
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