Scoring Formulas
Term Frequency (TF)
TF(t,d)=f_(t,d)/(∣d∣)

Where:
	f_(t,d)= frequency of term t in document d
	∣d∣= total tokens in document
________________________________________
Inverse Document Frequency (IDF)
IDF(t)=log⁡(N/(df_t ))

Where:
	N = total number of documents
	df_t= number of documents containing term t
________________________________________
TF-IDF
TFIDF(t,d)=TF(t,d)×IDF(t)

________________________________________
BM25
BM25(t,d)=IDF(t)⋅(f_(t,d) (k_1+1))/(f_(t,d)+k_1 (1-b+b (∣d∣)/avgdl) )

Where:
	k_1= term saturation parameter
	b= length normalization parameter
	avgdl= average document length
________________________________________
Cosine Similarity
"sim"(A,B)=(A⋅B)/(∥A∥∥B∥)

