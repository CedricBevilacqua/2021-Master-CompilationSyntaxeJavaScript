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
functionParam = dict() #Nom des paramètres des fonctions dans l'ordre où elles ont été chargées afin de pouvoir donner un nom aux arguments
functionVar = [] #Liste de dictionnaires des variables pour chaque fonction en cours d'exécution
functionMemory = dict() #Contient le nom et le contenu de chaque fonction
functionNumberEtiquette = dict() #Liste des fonctions à écrire
execPile = []

numGlobalVar = [0]
numEtiquette = [0]


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
                    print("#include \"base.h\"")
                    print("int main() {")
                    print("init(8192, 0, 8192);")
                    parcours_program(value2, 0, True)
                    print("goto END;")
                    print_etiquettes()
                    print("END:")
                    print("return 0;")
                    print('}')

def print_etiquettes():
    for key, value in functionNumberEtiquette.items():
        for boucle in range(value):
            print(key + str(boucle) + ':')
            parcours_program(functionMemory[key], 0, True)
            print("goto RETURN" + key + str(boucle) + ";")

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
            text += "endif" + str(numEtiquette[0]) + ":" + "\n"
            numEtiquette[0] = numEtiquette[0] + 1
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
            functionMemory[value["id"]["name"]] = value["body"]["body"]
            paramTab = []
            for param in value["params"]:
                paramTab.append(param["name"])
            functionParam[value["id"]["name"]] = paramTab
            functionNumberEtiquette[value["id"]["name"]] = 0
        elif value["type"] == "ReturnStatement":
            if(value["argument"] != None):
                askChange["return"] = (True,decoder_expression(value["argument"]))
            else:
                askChange["return"] = (True,None)
            if(printFlag == True):
                print(text)
            return text
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
        text = "push(iconst(" + str(data_dict["value"]) + "));\n"
        return text
    elif data_dict["type"] == "BinaryExpression":
        calculLeft  = decoder_expression(data_dict["left"])
        calculRight = decoder_expression(data_dict["right"])
        if(calculRight != None and calculLeft != None):
            text = ""
            text += str(calculLeft) + "\n"
            text += str(calculRight) + "\n"
            text += "pop(r1);" + "\n"
            text += "pop(r2);" + "\n"
            if(data_dict["operator"] == "+"):
                text += "iadd(r1,r2,r1);" + "\n"
                text += "push(r1);" + "\n"
                return text
            elif(data_dict["operator"] == "-"):
                text += "isub(r1,r2,r1);" + "\n"
                text += "push(r1);" + "\n"
                return text
            elif(data_dict["operator"] == "*"):
                text += "imul(r1,r2,r1);" + "\n"
                text += "push(r1);" + "\n"
                return text
            elif(data_dict["operator"] == "/"):
                text += "idiv(r1,r2,r1);" + "\n"
                text += "push(r1);" + "\n"
                return text
            elif(data_dict["operator"] == "<"):
                text += "ilt(r1,r2,r1);" + "\n"
                text += "push(r1);" + "\n"
                text += "pop(r1);" + "\n"
                text += "lneg(r1,r1);" + "\n"
                return text
            elif(data_dict["operator"] == "<="):
                text += "ile(r1,r2,r1);" + "\n"
                text += "push(r1);" + "\n"
                text += "pop(r1);" + "\n"
                text += "lneg(r1,r1);" + "\n"
                return text
            elif(data_dict["operator"] == ">"):
                text += "ilt(r1,r1,r2);" + "\n"
                text += "push(r1);" + "\n"
                text += "pop(r1);" + "\n"
                text += "lneg(r1,r1);" + "\n"
                return text
            elif(data_dict["operator"] == ">="):
                text += "ile(r1,r1,r2);" + "\n"
                text += "push(r1);" + "\n"
                text += "pop(r1);" + "\n"
                text += "lneg(r1,r1);" + "\n"
                return text
            elif(data_dict["operator"] == "=="):
                text += "ueq(r1,r1,r2);" + "\n"
                text += "push(r1);" + "\n"
                text += "pop(r1);" + "\n"
                text += "lneg(r1,r1);" + "\n"
                return text
            elif(data_dict["operator"] == "!="):
                text += "ueq(r1,r1,r2);" + "\n"
                text += "push(r1);" + "\n"
                return text
        else:
            print("Erreur l'une des variables est indéfini")
    elif data_dict["type"] == "Identifier":
        return "push(globals[" + str(variables[data_dict["name"]]) + "]);"
    elif data_dict["type"] == "UpdateExpression":
        text = ""
        if(data_dict["operator"] == "++"):
            if len(execPile) > 0 and data_dict["argument"]["name"] in functionVar[execPile[len(execPile)-1]].keys():
                functionVar[execPile[len(execPile)-1]][data_dict["argument"]["name"]] = functionVar[execPile[len(execPile)-1]][data_dict["argument"]["name"]] + 1
            else:
                text += "push(globals[" + str(variables[data_dict["argument"]["name"]]) + "]);" + "\n"
                text += "push(iconst(1));" + "\n"
                text += "pop(r1);" + "\n"
                text += "pop(r2);" + "\n"
                text += "iadd(r1,r2,r1);" + "\n"
                text += "globals[" + str(variables[data_dict["argument"]["name"]]) + "] = r1;" + "\n"
        elif(data_dict["operator"] == "--"):
            if len(execPile) > 0 and data_dict["argument"]["name"] in functionVar[execPile[len(execPile)-1]].keys():
                functionVar[execPile[len(execPile)-1]][data_dict["argument"]["name"]] = functionVar[execPile[len(execPile)-1]][data_dict["argument"]["name"]] + 1
            else:
                text += "push(globals[" + str(variables[data_dict["argument"]["name"]]) + "]);" + "\n"
                text += "push(iconst(1));" + "\n"
                text += "pop(r1);" + "\n"
                text += "pop(r2);" + "\n"
                text += "isub(r1,r2,r1);" + "\n"
                text += "globals[0] = r1;" + "\n"
        return text
    elif data_dict["type"] == "CallExpression":
        text = ""
        if(data_dict["callee"]["name"] == "print"):
            text += "push(globals[" + str(variables[data_dict["arguments"][0]["name"]]) + "]);" + "\n"
            text += "pop(r1);" + "\n"
            text += "debug_reg(r1);" + "\n"
        else:
            text += "goto "
            text += data_dict["callee"]["name"] + str(functionNumberEtiquette[data_dict["callee"]["name"]])
            text += ";"
            text += "\n"
            text += "RETURN" + data_dict["callee"]["name"] + str(functionNumberEtiquette[data_dict["callee"]["name"]]) + ":"
            text += "\n"
            functionNumberEtiquette[data_dict["callee"]["name"]] = functionNumberEtiquette[data_dict["callee"]["name"]] + 1
        return text
    elif data_dict["type"] == "AssignmentExpression":
        text = ""
        if(data_dict["operator"] == "="):
            if len(execPile) > 0 and data_dict["left"]["name"] in functionVar[execPile[len(execPile)-1]].keys():
                functionVar[execPile[len(execPile)-1]][data_dict["left"]["name"]] = decoder_expression(data_dict["right"])
            else:
                text += decoder_expression(data_dict["right"])
                text += "pop(r1);" + "\n"
                text += "globals[" + str(variables[data_dict["left"]["name"]]) + "] = r1;" + "\n"
        elif(data_dict["operator"] == "+="):
            if len(execPile) > 0 and data_dict["left"]["name"] in functionVar[execPile[len(execPile)-1]].keys():
                functionVar[execPile[len(execPile)-1]][data_dict["left"]["name"]] = functionVar[execPile[len(execPile)-1]][data_dict["left"]["name"]] + decoder_expression(data_dict["right"])
            else:
                text += decoder_expression(data_dict["right"])
                text += "pop(r1);" + "\n"
                text += "push(globals[0]);" + "\n"
                text += "pop(r2);" + "\n"
                text += "iadd(r1, r1, r2);" + "\n"
                text += "globals[" + str(variables[data_dict["left"]["name"]]) + "] = r1;" + "\n"
        elif(data_dict["operator"] == "-="):
            if len(execPile) > 0 and data_dict["left"]["name"] in functionVar[execPile[len(execPile)-1]].keys():
                functionVar[execPile[len(execPile)-1]][data_dict["left"]["name"]] = functionVar[execPile[len(execPile)-1]][data_dict["left"]["name"]] - decoder_expression(data_dict["right"])
            else:
                text += decoder_expression(data_dict["right"])
                text += "pop(r1);" + "\n"
                text += "push(globals[0]);" + "\n"
                text += "pop(r2);" + "\n"
                text += "isub(r1, r1, r2);" + "\n"
                text += "globals[" + str(variables[data_dict["left"]["name"]]) + "] = r1;" + "\n"
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
        kindVariables[value["id"]["name"]] = kindVar
        if(value["init"] != None):
            if(value["init"]["type"] != "NullLiteral"):
                if len(execPile) > 0:
                    functionVar[execPile[len(execPile)-1]][value["id"]["name"]] = value["init"]['value']
                else:
                    variables[value["id"]["name"]] = numGlobalVar[0]
                    if value["init"]["type"] == "NumericLiteral":
                        text += "globals[" + str(numGlobalVar[0]) + "] = iconst(" + str(value["init"]['value']) + ');'
                    elif value["init"]["type"] == "StringLiteral":
                        text += "globals[" + str(numGlobalVar[0]) + "] = " + "aconst(\"" + str(value["init"]['value']) + "\")" + ';'
                    numGlobalVar[0] = numGlobalVar[0] + 1
            else:
                if len(execPile) > 0:
                    functionVar[execPile[len(execPile)-1]][value["id"]["name"]] = None
                else:
                    variables[value["id"]["name"]] = numGlobalVar[0]
                    text += "globals[" + str(numGlobalVar[0]) + "] = aconst(NULL)" + ';'
                    numGlobalVar[0] = numGlobalVar[0] + 1
        else:
            if len(execPile) > 0:
                functionVar[execPile[len(execPile)-1]][value["id"]["name"]] = None
            else:
                variables[value["id"]["name"]] = numGlobalVar[0]
                text += "globals[" + str(numGlobalVar[0]) + "] = aconst(NULL)" + ';'
                numGlobalVar[0] = numGlobalVar[0] + 1
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
        text = "debut" + str(numEtiquette[0]) + ":" + '\n'
        text += decoder_expression(test_dict) + '\n'
        text += "if(asbool(r1)) goto endBoucle" + str(numEtiquette[0]) + ";" + '\n'
        text += parcours_program(data_tab, indentLevel, False)
        text += "goto debut" + str(numEtiquette[0]) + ";" + '\n'
        text += "endBoucle" + str(numEtiquette[0]) + ":" + '\n'
        numEtiquette[0] = numEtiquette[0] + 1
        return text
    elif(instruction == "if"):
        text = decoder_expression(test_dict) + '\n'
        text += "if(asbool(r1)) goto else" + str(numEtiquette[0]) + ";" + '\n'
        text += parcours_program(data_tab, indentLevel, False)
        text += "goto endif" + str(numEtiquette[0]) + ";\n"
        text += "else" + str(numEtiquette[0]) + ":" + "\n"
        return text
    elif(instruction == "else"):
        text = parcours_program(data_tab, indentLevel, False)
        return text
    return ""

def decoder_call(instruction_dict, args_tab):
    text = ""
    if(instruction_dict["name"] == "print"):
        text += "push(globals[" + str(variables[args_tab[0]["name"]]) + "]);" + "\n"
        text += "pop(r1);" + "\n"
        text += "puts(r1.a);" + "\n"
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

#Démarrage du décodage
datas = load_json(sys.argv[1])
parcours_main(datas)
