import chromadb

# client = chromadb.Client()


client = chromadb.PersistentClient(path="./chroma_db")  # saves to disk
collection = client.create_collection("my_collection",get_or_create = True)
collection.add(
    documents=["Banana is Fruit","Grapes is Fruit","Apple is fruit","Dog is animal","Mango is Fruit"],
    ids = ["1","2","123","234","345"]
)

result = collection.query(query_texts=["What is Fruit?"],n_results=10)
print(type(result))
print(result)
print(result['documents'])