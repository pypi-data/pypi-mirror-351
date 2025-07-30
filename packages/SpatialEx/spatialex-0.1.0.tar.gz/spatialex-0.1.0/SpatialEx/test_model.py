import os

from SpatialEx_pyG import Train_SpatialExP, Train_SpatialEx
import scanpy as sc

if __name__ == "__main__":
    # adata1 = sc.read_h5ad(
    #     os.path.join('./datasets/Human_Breast_Cancer_Rep1_uni_resolution64_full.h5ad'))
    # adata2 = sc.read_h5ad(
    #     os.path.join('./datasets/Human_Breast_Cancer_Rep2_uni_resolution64_full.h5ad'))
    #
    # model = Train_SpatialEx(adata1, adata2, device=8)
    # model.train()

    adata1 = sc.read_h5ad(
        os.path.join('./datasets/Human_Breast_Cancer_Rep1_uni_resolution64_genes1.h5ad'))
    adata2 = sc.read_h5ad(
        os.path.join('./datasets/Human_Breast_Cancer_Rep2_uni_resolution64_genes2.h5ad'))

    model = Train_SpatialExP(adata1, adata2, device=8)
    model.train()
