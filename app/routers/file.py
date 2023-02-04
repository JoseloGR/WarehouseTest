import pandas as pd
from fastapi import APIRouter, UploadFile, Response, HTTPException, status

router = APIRouter()

@router.post('/')
async def upload_file(file: UploadFile):
    try:    
        contents = await file.read()
        excel_data = pd.read_excel(contents)
        excel_data.fillna(value=0, inplace=True)
        list_data = excel_data.to_dict(orient='records')
        
        # for in
        filtered_dict = dict(filter(lambda elem: elem[1] != 0 or type(elem[1]) == str, list_data[0].items()))
        # check if Sub inventario key exists
        
        return Response(status_code=status.HTTP_200_OK)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=str(e))