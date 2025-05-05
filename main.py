from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import re

app = FastAPI(title="SMS MCP Server", description="A simple SMS MCP server for carrier detection")

class PhoneNumber(BaseModel):
    phone_number: str

def detect_carrier(phone_number: str) -> str:
    """
    检测手机号码的运营商
    这里使用简单的规则来判断，实际应用中可能需要更复杂的逻辑或数据库查询
    """
    # 移除所有非数字字符
    clean_number = re.sub(r'\D', '', phone_number)
    
    # 确保号码长度正确
    if len(clean_number) != 11:
        raise HTTPException(status_code=400, detail="Invalid phone number length")
    
    # 简单的运营商判断规则（仅作示例）
    prefix = clean_number[:3]
    if prefix in ['130', '131', '132', '133', '134', '135', '136', '137', '138', '139']:
        return "China Mobile"
    elif prefix in ['145', '147', '149', '150', '151', '152', '153', '155', '156', '157', '158', '159', '166', '167', '168', '170', '171', '172', '173', '174', '175', '176', '177', '178', '180', '181', '182', '183', '184', '185', '186', '187', '188', '189']:
        return "China Unicom"
    elif prefix in ['133', '149', '153', '173', '177', '180', '181', '189', '199']:
        return "China Telecom"
    else:
        return "Unknown Carrier"

@app.post("/detect-carrier")
async def detect_carrier_endpoint(phone: PhoneNumber):
    """
    检测手机号码的运营商
    """
    try:
        carrier = detect_carrier(phone.phone_number)
        return {"phone_number": phone.phone_number, "carrier": carrier}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """
    根路径，返回简单的欢迎信息
    """
    return {"message": "Welcome to SMS MCP Server", "status": "running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 