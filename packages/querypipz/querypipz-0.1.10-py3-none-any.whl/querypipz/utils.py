class VisualIndex():
    def __init__(self,index):
        self.index = index

    def get_docs_id(self):
        return list(self.index.docstore.docs.keys())

    def get_documents(self):
        return [self.index.docstore.get_document(i) for i in self.get_docs_id()]

    def get_document_by_id(self,doc_id): # 有a功能
        return self.index.docstore.get_document(doc_id)
