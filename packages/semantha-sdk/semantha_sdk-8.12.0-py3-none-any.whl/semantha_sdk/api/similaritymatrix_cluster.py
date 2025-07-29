from semantha_sdk.model.matrix_row import MatrixRow
from semantha_sdk.model.matrix_row import MatrixRowSchema
from semantha_sdk.model.mode_enum import ModeEnum
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint
from typing import List

class SimilaritymatrixClusterEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/domains/{domainname}/similaritymatrix/cluster"
    author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/cluster"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)

    
    def post(
        self,
        tags: str = None,
        documentids: List[str] = None,
        documentclassids: List[str] = None,
        similaritythreshold: float = None,
        mode: ModeEnum = None,
        considertexttype: bool = None,
    ) -> List[MatrixRow]:
        """
        Get document clusters
            Consolidate the documents to clusters based on the results of `post post /api/domains/{domainname}/similaritymatrix`
        Args:
        tags (str): List of tags to filter the reference library. You can combine the tags using a comma (OR) and using a plus sign (AND).
    documentids (List[str]): List of document Ids for target. The limit here is 65000 IDs.
            The IDs are passed as a JSON array.
    documentclassids (List[str]): List of documentclass IDs for the target. The limit here is 1000 IDs.
            The IDs are passed as a JSON array.
            This does not apply on the GET referencedocuments call. Here the ids are separated with a comma.
    similaritythreshold (float): Threshold for the similarity score. semantha will not deliver results with a sentence score lower than the threshold.
            In general, the higher the threshold, the more precise the results.
    mode (ModeEnum): When using the references endpoint: Use mode to determine the type of search semantha should perform. 
            fingerprint: semantic search based on sentences; 
            keyword: keyword: search based on sentences; 
            document: a bag-of-words search that ranks a set of documents based on the query terms appearing in each document, regardless of their proximity within the document. Higher scores indicate higher similarity. Please note that the similarity score has no upper limit and is not normalized; 
            document_fingerprint: a bag-of-words search that ranks a set of documents based on the query terms appearing in each document, regardless of their proximity within the document. The results are then reranked based on a semantic search. This reranking results in normalized scores and as such represents an enhancement of the mode document; 
            fingerprint_keyword (formerly auto): semantic search, if no results are found a keyword search is performed
            Creating document model: It also defines what structure should be considered for what operator (similarity or extraction).
    considertexttype (bool): Use this parameter to ensure that only paragraphs of the same type are compared with each other. The parameter is of type boolean and is set to false by default.
        """
        q_params = {}
        response = self._session.post(
            url=self._endpoint,
            body={
                "tags": tags,
                "documentids": documentids,
                "documentclassids": documentclassids,
                "similaritythreshold": similaritythreshold,
                "mode": mode,
                "considertexttype": considertexttype,
            },
            headers=RestClient.to_header(MediaType.JSON),
            q_params=q_params
        ).execute()
        return response.to(MatrixRowSchema)
    def post_json(
        self,
        body: List[MatrixRow] = None,
    ) -> List[MatrixRow]:
        """
        Get document clusters
            Consolidate the documents to clusters based on the results of `post post /api/domains/{domainname}/similaritymatrix`
        Args:
        body (List[MatrixRow]): 
        """
        q_params = {}
        response = self._session.post(
            url=self._endpoint,
            json=MatrixRowSchema().dump(body, many=True),
            headers=RestClient.to_header(MediaType.JSON),
            q_params=q_params
        ).execute()
        return response.to(MatrixRowSchema)

    
    
    