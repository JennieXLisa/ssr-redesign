"""Pure UTF-8 reference model for sizing/replay tests; no Git or database I/O.

Production must additionally implement other codecs and authoritative DB access.
"""
from __future__ import annotations
import base64
import json
from dataclasses import dataclass
from typing import Any

MAX = 2**63 - 1

def compact(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(',', ':')).encode('utf-8')

def encode(payload: dict) -> str:
    return 'ssr1.' + base64.urlsafe_b64encode(compact(payload)).decode('ascii').rstrip('=')

def no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate token key')
        result[key] = value
    return result

def decode(token: str) -> dict:
    if len(token.encode('utf-8')) > 4096 or not token.startswith('ssr1.'):
        raise ValueError('invalid token encoding')
    raw = token[5:]
    if not raw or any(c not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_' for c in raw):
        raise ValueError('invalid base64url token')
    return json.loads(base64.urlsafe_b64decode(raw + '='*((-len(raw)) % 4)), object_pairs_hook=no_duplicates)

@dataclass(frozen=True)
class Subject:
    data: bytes
    path: str
    run: str
    snapshot: str
    file: str
    symbol: str
    occurrence: str

    def payload(self, start, end, budget):
        return dict(v=1,type='source',subject_kind='function',index_run_id=self.run,
            snapshot_id=self.snapshot,file_id=self.file,symbol_id=self.symbol,
            occurrence_id=self.occurrence,selection_start=0,selection_end=len(self.data),
            page_start=start,page_end=end,budget=budget,reader_profile='source-v1')

    def position(self, offset):
        # Byte validation happens through strict UTF-8 decoding of the prefix.
        text = self.data[:offset].decode('utf-8')
        if text.startswith('\ufeff'):
            text = text[1:]
        line, col, i = 1, 1, 0
        while i < len(text):
            if text[i] == '\r':
                i += 1
                if i < len(text) and text[i] == '\n':
                    i += 1
                line, col = line+1, 1
            elif text[i] == '\n':
                i += 1;line,col = line+1,1
            else:
                i += 1;col += 1
        return line, col

    def response(self, start, end, next_token, coverage):
        sl,sc=self.position(start);el,ec=self.position(end)
        return dict(subject_kind='function',index_run_id=self.run,snapshot_id=self.snapshot,
            symbol_id=self.symbol,occurrence_id=self.occurrence,path=self.path,
            source=self.data[start:end].decode('utf-8'),
            range=dict(start_byte=start,end_byte=end,start_line=sl,end_line=el,start_column=sc,end_column=ec),
            next_continuation=next_token,coverage=coverage)

    def reserve(self, budget):
        payload=self.payload(MAX-1,MAX,1_000_000)
        payload['selection_start']=MAX-1;payload['selection_end']=MAX
        worst={'index_complete':False,**{k:dict(total_files=MAX,completed_files=MAX,failed_files=MAX) for k in ('extraction','resolution','flagging')}}
        template=self.response(0,0,encode(payload),worst)
        template['range']={k:MAX for k in template['range']}
        return len(compact(template))

    def atoms(self, start=0):
        text=self.data[start:].decode('utf-8');i=0;pos=start
        while i < len(text):
            atom=text[i]
            if atom=='\r' and i+1<len(text) and text[i+1]=='\n':
                atom='\r\n';i+=1
            i+=1;pos+=len(atom.encode('utf-8'))
            yield atom,pos

    def interval(self, start, budget):
        allowance=budget-self.reserve(budget)
        end=start;last_line=None;used=0
        for atom,boundary in self.atoms(start):
            size=len(compact(atom))-2  # Remove the JSON string's quotes.
            if used+size > allowance:
                break
            used+=size;end=boundary
            if atom in ('\r','\n','\r\n'):
                last_line=end
        if end < len(self.data) and last_line is not None:
            end=last_line
        if end==start and end<len(self.data):
            raise ValueError('RESPONSE_BUDGET_TOO_SMALL')
        return start,end

    def minimum(self, budget, coverage):
        if not self.data:
            return len(compact(self.response(0,0,None,coverage)))
        return self.reserve(budget)+max((len(compact(atom))-2 for atom,_ in self.atoms()),default=0)

    def initial(self,budget,coverage):
        if isinstance(budget,bool) or not 1<=budget<=1_000_000:
            raise ValueError('INVALID_ARGUMENT')
        if budget<self.minimum(budget,coverage):
            raise ValueError('RESPONSE_BUDGET_TOO_SMALL')
        start,end=self.interval(0,budget)
        return self.render(start,end,budget,coverage)

    def render(self,start,end,budget,coverage):
        nxt=None
        if end<len(self.data):
            ns,ne=self.interval(end,budget);nxt=encode(self.payload(ns,ne,budget))
        result=self.response(start,end,nxt,coverage)
        if len(compact(result))>budget:
            raise AssertionError('whole-response budget violated')
        return result

    def continuation(self,token,coverage):
        payload=decode(token)
        required=self.payload(payload.get('page_start'),payload.get('page_end'),payload.get('budget'))
        if payload!=required:
            raise ValueError('INVALID_CONTINUATION')
        start,end=payload['page_start'],payload['page_end'];budget=payload['budget']
        if not isinstance(start,int) or not isinstance(end,int) or not 0<=start<end<=len(self.data):
            raise ValueError('INVALID_CONTINUATION')
        if self.interval(start,budget)!=(start,end):
            raise ValueError('INVALID_CONTINUATION')
        return self.render(start,end,budget,coverage)
