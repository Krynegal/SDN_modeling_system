import requests as req

USER = ("onos", "rocks")

def clearFlows():
    res = req.delete(f"http://172.17.0.2:8181/onos/v1/flows/application/org.onosproject.rest", auth=USER)
    if res.status_code == 204:
        print("flows rest are deleted")
    else:
        print("can not delete rest flows")
def clearFwdFlows():
    res = req.delete(f"http://172.17.0.2:8181/onos/v1/flows/application/org.onosproject.fwd", auth=USER)
    if res.status_code == 204:
        print("flows fwd are deleted")
    else:
        print("can not delete fwd flows")

if __name__ == '__main__':
    clearFlows()
    clearFwdFlows()