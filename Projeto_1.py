"""
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterDistance)
from qgis import processing


class CartaTrafegabilidade(QgsProcessingAlgorithm):

    VIA = 'VIA' #Camada da via
    RVIA='RVIA' # raio do buffer da via 
    VGT = 'VGT' # camada vegetação 
    MDA = 'MDA' # Camada Massa d'água
    TD = 'TD'   # Camada Trecho de drenagem 
    RTD ='RTD'  # Raio do buffer do trecho de drenagem 
    RMC ='RMC'  # Raio do buffer mata ciliar 
    AED ='AED'  # Camada Área edificada
    ASD ='ASD'  # Área sem dados 
    MDT = 'MDT' # MDT
    TP = 'TP'   # Tamanho do pixel 
    OUTPUT = 'OUTPUT'

    def tr(self, string):
    
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return CartaTrafegabilidade()

    def name(self):
        return 'cartatrafegabilidade'

    def displayName(self):
        return self.tr('Projeto 1')

    def group(self):
        return self.tr('Projeto')

    def groupId(self):
        return 'examplescripts'

    def shortHelpString(self):
        return self.tr("Projeto para identificação de trafegabilidade")

    def initAlgorithm(self, config=None):

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.VIA,
                self.tr('Camada Via de deslocamento'),
                [QgsProcessing. TypeVectorLine]
            )
        )
        
        self.addParameter (
            QgsProcessingParameterDistance (
                self.RVIA,
                self.tr('Buffer para a via de deslocamento' ),
                parentParameterName =self.VIA ,
                minValue=0,
                defaultValue =1.0
            )
)

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.VGT,
                self.tr('Camada Vegetação'),
                [QgsProcessing.TypeVectorPolygon]
            )
        )
        
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.MDA,
                self.tr("Camada Massa d'agua "),
                [QgsProcessing.TypeVectorPolygon]
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.TD,
                self.tr('Camada Trecho de Drenagem'),
                [QgsProcessing.TypeVectorLine]
            )
        )
        
        self.addParameter (
            QgsProcessingParameterDistance (
                self.RTD,
                self.tr('Buffer Trecho de deslocamento' ),
                parentParameterName =self.TD ,
                minValue=0,
                defaultValue =1.0
            )
)       
        self.addParameter (
            QgsProcessingParameterDistance (
                self.RMC,
                self.tr('Buffer da Mata ciliar' ),
                parentParameterName =self.VGT ,
                minValue=0,
                defaultValue =1.0
            )
)    

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.AED,
                self.tr("Camada Área edificada"),
                [QgsProcessing.TypeVectorPolygon]
            )
        )   

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.ASD,
                self.tr("Camada Área sem dados"),
                [QgsProcessing.TypeVectorPolygon]
            )
        )

        self.addParameter (
            QgsProcessingParameterDistance (
                self.RTD,
                self.tr('Buffer Trecho de deslocamento' ),
                parentParameterName =self.TD ,
                minValue=0,
                defaultValue =1.0
            )
)    

        self.addParameter (
            QgsProcessingParameterDistance (
                self.TP,
                self.tr('Tamanho do pixel'),
                parentParameterName =self.MDT ,
                minValue=0,
                defaultValue =1.0
            )
)           
        
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.MDT,
                self.tr("Camada MDT"),
                [QgsProcessing.TypeRaster]
            )
        )   
        

        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Output layer')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        vias = self.parameterAsSource(
            parameters,
            self.VIA,
            context
        )

        mdagua = self.parameterAsSource(
            parameters,
            self.MDA,
            context
        )

        areaEdificada = self.parameterAsSource(
            parameters,
            self.AED,
            context
        )

        vegetacao = self.parameterAsSource(
            parameters,
            self.VGT,
            context
        )

        trechoDrenagem = self.parameterAsSource(
            parameters,
            self.TD,
            context
        )



        raioVia = self.parameterAsDouble(
            parameters, 
            self.RVIA,
            context
        )

        raioTrechoDrenagem =  self.parameterAsDouble(
            parameters, 
            self.RTD,
            context
        )

        raioMataCiliar =  self.parameterAsDouble(
            parameters, 
            self.RMC,
            context)
        
        # If source was not found, throw an exception to indicate that the algorithm
        # encountered a fatal error. The exception text can be any string, but in this
        # case we use the pre-built invalidSourceError method to return a standard
        # helper text for when a source cannot be evaluated
        if vias is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))

        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            vias.fields(),
            vias.wkbType(),
            vias.sourceCrs()
        )

        # Send some information to the user
        feedback.pushInfo(f'CRS is {vias.sourceCrs().authid()}')

        # If sink was not created, throw an exception to indicate that the algorithm
        # encountered a fatal error. The exception text can be any string, but in this
        # case we use the pre-built invalidSinkError method to return a standard
        # helper text for when a sink cannot be evaluated
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        # Compute the number of steps to display within the progress bar and
        # get features from source
        total = 100.0 / vias.featureCount() if vias.featureCount() else 0
        features = vias.getFeatures()

        for current, feature in enumerate(features):
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                break

            # Add a feature in the sink
            sink.addFeature(feature, QgsFeatureSink.FastInsert)

            # Update the progress bar
            feedback.setProgress(int(current * total))

        #Obter via de deslocamento 
        viaDeslocamento = processing.run("native:buffer", 
            {'INPUT':vias,
             'DISTANCE':raioVia,
             'SEGMENTS':5,
             'END_CAP_STYLE':0,
             'JOIN_STYLE':0,
             'MITER_LIMIT':2,
             'DISSOLVE':False,
             'SEPARATE_DISJOINT':False,
             'OUTPUT':'TEMPORARY_OUTPUT'})

        #Obter o trecho de drenagem 
        
        trechoDrenagemFinal = processing.run("native:buffer", 
            {'INPUT':trechoDrenagem,
             'DISTANCE':raioTrechoDrenagem,
             'SEGMENTS':5,
             'END_CAP_STYLE':0,
             'JOIN_STYLE':0,
             'MITER_LIMIT':2,
             'DISSOLVE':False,
             'SEPARATE_DISJOINT':False,
             'OUTPUT':'TEMPORARY_OUTPUT'})
        
        # Obter mata ciliar 
        mataCiliarFinal = processing.run("native:buffer", 
            {'INPUT':vegetacao,
             'DISTANCE':raioMataCiliar,
             'SEGMENTS':5,
             'END_CAP_STYLE':0,
             'JOIN_STYLE':0,
             'MITER_LIMIT':2,
             'DISSOLVE':False,
             'SEPARATE_DISJOINT':False,
             'OUTPUT':'TEMPORARY_OUTPUT'})
        
        # Extrair Vias de deslocamento federal
        viaFederal = processing.run("native:extractbyexpression", 
               {'INPUT':viaDeslocamento,
                'EXPRESSION':'"tipo" = 2 and  "jurisdicao" =1',
                 'OUTPUT':'TEMPORARY_OUTPUT'}) 
        
        return {self.OUTPUT: dest_id}
