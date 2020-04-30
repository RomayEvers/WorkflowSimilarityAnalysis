# [TODO] input1, input2, input3 => input; the same for outputs
# [TODO] excluded
#       - WallplantsPC4 kopie.ttl: same IO for operations
#       - WaterPC4 kopie.ttl: same IO for operations
# [TODO] EnergylabelPC4 kopie.ttl: corrected output
# [TODO] excluded edges: ParksandgreenPC4 kopie.ttl, ResidentialcarehomesPC4 kopie.ttl, TreedensityPC4 kopie.ttl,
# [TODO] duplicate tools or tools with similar functionality?
#   - https://desktop.arcgis.com/en/arcmap/latest/tools/spatial-analyst-toolbox/zonal-statistics-as-table.htm;G
#   - https://pro.arcgis.com/en/pro-app/tool-reference/spatial-analyst/zonal-statistics-as-table.htm;5
#` [TODO] multiple comments`


# [TODO] duplicate wf:edge triple _:wf1_4
# [TODO] TreedensityPC4, WaterPC4 => input1, input2
# [TODO] WOZAmsterdam duplicate comment
# [TODO] SubwayAmstrdam: tool => tools
# [TODO] WaterPC4: water-area => water_area
# [TODO] WaterPC4, EnergylabelPC4: ouput => output
# [TODO] changed comments: BAGPC4


import re
import csv

from os import walk

from rdflib import Graph
from rdflib import URIRef
from rdflib.namespace import RDF
from rdflib.namespace import RDFS
import pprint

def parseWhatQuestions():
    nonobjects = ('and', ',', '-', 'a', 'the', ')', '(')

    subExpress = "\S+"
    subMatcher = re.compile(subExpress, re.IGNORECASE)

    intentExpr = (
            "What "  # required wh start (case insensitive)
            + "(is|are|were|was|do|does|did|have|has|should|could|would|will) (be )?"  # required auxiliary
            + "(the |a )?"  # optional article
            + "(?P<adjective>(.*?))"  # lazy matching any zero or more chars
            + "(?P<intent>\S+)"  # any non-white space char
            + "(?P<rightside> (across|along|among|around|at|based on|based upon|between|by|for|from|given|if|in|inside|of|on|over|per|since|that|to|with|within) (.+))"
    )
    intentMatcher = re.compile(intentExpr, re.IGNORECASE)

    extentExpr = (
            "(?P<objectphrase>.*?)"
            + "(?P<relation> (across|along|among|around|at|between|by|for|from|in|inside|of|on|per|to|within)) "
            + "(?P<extent>((?! (across|along|among|around|at|between|by|for|from|in|inside|of|on|per|to|within) ).)*)$"
    )
    extentMatcher = re.compile(extentExpr, re.IGNORECASE)

    simpleObjExp = (
            "(?P<relation>(across|along|among|around|at|based on|based upon|between|by|for|from|given|in|inside|of|on|over|per|since|that|to|with|within) )"
            + "(?P<object>.*)"  # lazy matching any zero or more chars
    )
    simpleObjMatcher = re.compile(simpleObjExp, re.IGNORECASE)

    wfCount = 0

    # [SC] writes detected intent to this file as table with intent and question id
    with open(f"{dataOutputDir}\\what_questions.csv", 'w', newline='') as questioncsvfile:
        questionwriter = csv.DictWriter(questioncsvfile, delimiter=';', fieldnames=['question', 'qid'])
        questionwriter.writeheader()

        with open(f"{dataOutputDir}\\what_intents.csv", 'w', newline='') as intentcsvfile:
            intentwriter = csv.DictWriter(intentcsvfile, delimiter=';', fieldnames=['intent', 'qid'])
            intentwriter.writeheader()

            with open(f"{dataOutputDir}\\what_objects.csv", 'w', newline='') as objcsvfile:
                objwriter = csv.DictWriter(objcsvfile, delimiter=';', fieldnames=['intent', 'relation', 'object', 'distance', 'qid'])
                objwriter.writeheader()

                with open(f"{dataOutputDir}\\what_adjectives.csv", 'w', newline='') as adjcsvfile:
                    adjwriter = csv.DictWriter(adjcsvfile, delimiter=';', fieldnames=['intent', 'adjective', 'distance', 'qid'])
                    adjwriter.writeheader()

                    with open(f"{dataOutputDir}\\what_extents.csv", 'w', newline='') as extentcsvfile:
                        extentwriter = csv.DictWriter(extentcsvfile, delimiter=';', fieldnames=['relation', 'extent', 'qid'])
                        extentwriter.writeheader()

                        for workflowFile in wfFilenames:
                            print(f"Parsing file {workflowFile}")

                            g = Graph()
                            g.parse(f"{workflowDataDir}\\{workflowFile}", format="turtle")

                            for s, p, o in g.triples((None, RDF.type, wfType)):
                                wfCount += 1
                                q = g.value(s, RDFS.comment)
                                qId = f"WF-{wfCount}"
                                # print("{} is a workflow for {}".format(s, q))

                                questionwriter.writerow({
                                    'question': q
                                    , 'qid': qId
                                })

                                intentResult = intentMatcher.search(q)
                                if intentResult:
                                    intentwriter.writerow({
                                        'intent': intentResult.group('intent')
                                        , 'qid': qId
                                    })

                                    if intentResult.group('adjective'):
                                        # [SC] write to file the entire adjective phrase at first
                                        adjwriter.writerow({
                                            'intent': intentResult.group('intent')
                                            , 'adjective': intentResult.group('adjective')
                                            , 'distance': 0
                                            , 'qid': qId
                                        })

                                        # [SC] extract and save to a file individual adjective words from the phrase
                                        subResults = subMatcher.findall(intentResult.group('adjective'))
                                        for adjCount in range(len(subResults)):
                                            if subResults[adjCount] not in nonobjects:
                                                adjwriter.writerow({
                                                    'intent': intentResult.group('intent')
                                                    , 'adjective': subResults[adjCount]
                                                    , 'distance': len(subResults) - adjCount
                                                    , 'qid': qId
                                                })

                                    extentResult = extentMatcher.search(intentResult.group('rightside'))
                                    if extentResult:
                                        extentwriter.writerow({
                                            'relation': extentResult.group('relation').strip()
                                            , 'extent': extentResult.group('extent').strip()
                                            , 'qid': qId
                                        })

                                        if extentResult.group('objectphrase'):
                                            simpleObjResult = simpleObjMatcher.search(extentResult.group('objectphrase'))

                                            print(q)
                                            print(extentResult.group('objectphrase'))
                                            print(simpleObjResult.group('relation'))
                                            print(simpleObjResult.group('object'))
                                            print("")

                                            # [SC] write to file the entire object phrase at first
                                            objwriter.writerow({
                                                'intent': intentResult.group('intent')
                                                , 'relation': simpleObjResult.group('relation').replace(' ', '')
                                                , 'object': simpleObjResult.group('object')
                                                , 'distance': 0
                                                , 'qid': qId
                                            })

                                            # [SC] extract and save to a file individual object words from the phrase
                                            subResults = subMatcher.findall(simpleObjResult.group('object'))
                                            for objectCount in reversed(range(len(subResults))):
                                                if subResults[objectCount] not in nonobjects:
                                                    objwriter.writerow({
                                                        'intent': intentResult.group('intent')
                                                        , 'relation': simpleObjResult.group('relation').replace(' ', '')
                                                        , 'object': subResults[objectCount]
                                                        , 'distance': len(subResults) - objectCount
                                                        , 'qid': qId
                                                    })


def extractUniqueTools():
    asciiChars = list(range(48, 58))
    asciiChars.extend(range(65, 91))
    asciiChars.extend(range(97, 123))

    toolCount = 0

    toolDict.clear()

    # [SC] this file stores tool annotation with letters
    with open(f"{dataOutputDir}\\tools.csv", 'w', newline='') as toolcsvfile:
        toolwriter = csv.DictWriter(toolcsvfile, delimiter=';', fieldnames=['toolUri', 'letter'])
        toolwriter.writeheader()

        for workflowFile in wfFilenames:
            g = Graph()
            g.parse(f"{workflowDataDir}\\{workflowFile}", format="turtle")

            for s, p, o in g.triples((None, implementsP, None)):
                if str(o) not in toolDict:
                    # [SC] add tool to the dictionary
                    toolDict[str(o)] = chr(asciiChars[toolCount])
                    # [SC] add tool to the datafile
                    toolwriter.writerow({
                        'toolUri': str(o)
                        , 'letter': chr(asciiChars[toolCount])
                    })

                    toolCount += 1


def serializeWorkflow():
    with open(f"{dataOutputDir}\\serial_wfs.csv", 'w', newline='') as serialwfsvfile:
        wfswriter = csv.DictWriter(serialwfsvfile, delimiter=';', fieldnames=['question', 'qid', 'serial'])
        wfswriter.writeheader()

        wfCount = 0

        for wfFilename in wfFilenames:
            g = Graph()
            g.parse(f"{workflowDataDir}\\{wfFilename}", format="turtle")

            print(f"Serializing {wfFilename}")

            # [SC] iterate through workflows
            for s, p, o in g.triples((None, RDF.type, wfType)):
                # [SC] serialization of the workflow
                charList = []

                dataList = []
                dataList.extend(g.objects(s, sourceP))

                operations = []
                operations.extend(g.objects(s, edgeP))

                while len(operations) > 0:
                    tempList = []
                    operationRemoveList = []

                    for operation in operations:
                        canExecute = True

                        # [SC] all input data should be in dataList
                        for inputData in g.objects(operation, inputP):
                            if inputData not in dataList:
                                canExecute = False
                                break

                        if canExecute:
                            operationRemoveList.append(operation)

                    for operation in operationRemoveList:
                        toolUri = str(g.value(operation, implementsP))
                        tempList.append(toolDict[toolUri])

                        dataList.extend(g.objects(operation, inputP))
                        dataList.extend(g.objects(operation, outputP))

                        operations.remove(operation)

                    charList.append(tempList)

                    # print(dataList)
                    # print(charList)

                wfSerialization = ""
                for chars in charList:
                    chars.sort()
                    for char in chars:
                        wfSerialization += char;
                    wfSerialization += '|'

                wfCount += 1
                q = g.value(s, RDFS.comment)
                qId = f"WF-{wfCount}"

                wfswriter.writerow({
                    'question': q
                    , 'qid': qId
                    , 'serial': wfSerialization
                })

                print(wfSerialization)


# [SC] this function is for testing purpose only
def testSerializeWorkflow():
    g = Graph()
    g.parse(f"{workflowDataDir}\\WallplantsPC4 kopie.ttl", format="turtle")

    # [SC] for testing purpose only
    # for subj, pred, obj in g:
    #     print(subj)
    #     print(pred)
    #     print(obj)
    #     print("")

    # [SC] iterate through workflows
    for s, p, o in g.triples((None, RDF.type, wfType)):
        # [SC] serialization of the workflow
        charList = []

        dataList = []
        dataList.extend(g.objects(s, sourceP))

        operations = []
        operations.extend(g.objects(s, edgeP))

        while len(operations) > 0:
            # [SC] identify root operations in the workflow
            tempList = []
            operationRemoveList = []

            for operation in operations:
                canExecute = True

                # [SC] all input data should be in dataList
                for inputData in g.objects(operation, inputP):
                    if inputData not in dataList:
                        canExecute = False
                        break

                if canExecute:
                    operationRemoveList.append(operation)

            for operation in operationRemoveList:
                toolUri = str(g.value(operation, implementsP))
                tempList.append(toolDict[toolUri])

                dataList.extend(g.objects(operation, inputP))
                dataList.extend(g.objects(operation, outputP))

                operations.remove(operation)

            charList.append(tempList)

            print(charList)
            print(f"Data: {dataList}")
            print(f"Operations: {operations}")
            print("")

        wfSerialization = ""
        for chars in charList:
            chars.sort()
            for char in chars:
                wfSerialization += char;

        print(wfSerialization)


if __name__ == '__main__':
    # [SC] folder with input corpora
    workflowDataDir = "workflowData"
    # [SC] data output folder
    dataOutputDir = "pythonOutputData"

    # [SC] rdf type Workflow
    wfType = URIRef("http://geographicknowledge.de/vocab/Workflow.rdf#Workflow")
    # [SC] rdf property edge
    edgeP = URIRef("http://geographicknowledge.de/vocab/Workflow.rdf#edge")
    # [SC] rdf property input
    inputP = URIRef("http://geographicknowledge.de/vocab/Workflow.rdf#input")
    # [SC] rdf property output
    outputP = URIRef("http://geographicknowledge.de/vocab/Workflow.rdf#output")
    # [SC] rdf property implements
    implementsP = URIRef("http://geographicknowledge.de/vocab/GISTools.rdf#implements")
    # [SC] rdf property source
    sourceP = URIRef("http://geographicknowledge.de/vocab/Workflow.rdf#source")

    # [SC] extract list of filenames from the workflow data directory
    wfFilenames = []
    for (dirpath, dirnames, filenames) in walk(f"{workflowDataDir}"):
        wfFilenames.extend(filenames)
        break

    # [SC] remove any non .ttl file
    for wfFilename in wfFilenames:
        if not wfFilename.endswith(".ttl"):
            wfFilenames.remove(wfFilename)

    # [SC] extract intents from the string questions
    parseWhatQuestions()

    # [SC] create tool dictionary with unique letter for each tool
    toolDict = dict()
    extractUniqueTools()

    # [SC] serialize workflows
    serializeWorkflow()