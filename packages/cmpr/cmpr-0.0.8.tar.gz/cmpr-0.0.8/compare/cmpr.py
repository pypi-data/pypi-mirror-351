from deciml.deciml import deciml, getpr
from decimal import Decimal
from terminate import retrn


class tint:

    @classmethod
    def iwgrp(cls,li:list|tuple)->tuple[int,...]:
        '''
#### Returns a tuple of whole integers ( >= 0 ).
- **li**: List or tuple of numbers
        '''
        try:
            if (tli:=li.__class__.__name__)=='tuple' or tli=='list':
                ln=list()
                for i in li:
                    ln.append((vi:=cls.intw(i)))
                    if vi is None:raise Exception(str(i)+" is not a whole number");
                return tuple(ln)
            else:raise Exception;
        except Exception as e:retrn('c',e);
    
    # return true if i is valid element index
    @classmethod
    def ele(cls,i:list|tuple,ln:int|float,b=None)->int|tuple[int,...]:
        '''
#### Returns integer of "i" or tuple of integers ( if "i" contains indexes ).
- **i**: Value or list/tuple of values
- **ln**: Length to compare
        '''
        try:
            ln=cls.intn(ln)
            if ln is None:raise Exception;
            if not b:
                i=cls.intw(i)
                if i>ln-1:raise Exception(str(i)+" is more than "+str(ln-1));
                return i
            elif ((ti:=i.__class__.__name__)=='list' or ti=='tuple') and b is True:
                i=cls.iwgrp(i)
                if i is None:raise Exception;
                for j in i:
                    if j>ln-1:raise Exception(str(j)+" is more than "+str(ln-1));
                return i
            else:raise Exception("'{}' is not 'list'/'tuple'".format(ti))
        except Exception as e:retrn('c',e);

    # check and return whole numbers
    @classmethod
    def intw(cls,i)->int:
        '''
#### Returns an integer ( >= 0 ) for value.
- **i**: Value
        '''
        try:
            if (j:=int(i))<0:raise Exception(str(i)+" < 0");
            else:return j;
        except Exception as e:retrn('c',e);

    # check and return natural numbers
    @classmethod
    def intn(cls,i)->int:
        '''
#### Returns an integer ( > 0 ) for value.
- **i**: Value
        '''
        try:
            if (j:=int(i))>0:return j;
            else:raise Exception(str(i)+" < 0");
        except Exception as e:retrn('c',e);

    # check and return int
    @staticmethod
    def int(i)->int:
        '''
#### Returns an integer for value.
- **i**: Value
        '''
        try:return int(i);
        except Exception as e:retrn('c',"{}\nCannot convert to integer".format(e));


class tdeciml:

    @staticmethod
    def dall(li:list|list[list]|tuple[tuple]|tuple,__pr=getpr())->tuple[Decimal,...]|tuple[tuple[Decimal,...],...]:
        '''
#### Returns tuple of Decimal objects, tuple of Decimal objects.
- **li**: List or tuple of numbers, list or tuple of list or tuple of numbers
- **__pr**: Precision
        '''
        try:
            if (tli:=li.__class__.__name__)=='tuple' or tli=='list':
                if (tli0 := li[0].__class__.__name__)=='list' or tli0=='tuple':
                    li1=list()
                    for i in li:
                        li2=list()
                        for j in i:
                            if (j1:=deciml(j,__pr))!=Decimal('NaN') or j1!=Decimal('Inf') or j1!=Decimal('-Inf'):li2.append(j1);
                            else:raise Exception(str(j)+" is NaN/Inf/-Inf");
                        li1.append(tuple(li2))
                    return tuple(li1)
                else:
                    li1=list()
                    for i in li:
                        if (i1:=deciml(i,__pr))!=Decimal('NaN') or i1!=Decimal('Inf') or i1!=Decimal('-Inf'):li1.append(i1);
                        else:raise Exception(str(i)+" is NaN/Inf/-Inf");
                    return tuple(li1)
            else:raise Exception;
        except Exception as e:retrn('c',str(e));

    # return if positive float
    @staticmethod
    def decip(a,__pr=getpr())->Decimal:
        '''
#### Returns Decimal object ( greater than zero ) for value.
- **a**: Value
- **__pr**: Precision
        '''
        try:
            if (an:=deciml(a,__pr))>0 or an!=Decimal('NaN') or an!=Decimal('Inf') or an!=Decimal('-Inf'):return an;
            else:raise Exception(str(a)+" is <=0/NaN/Inf/-Inf");  
        except Exception as e:retrn('c',e);

    @staticmethod
    def deciml(a:list|tuple,b=None)->bool:
        '''
#### Returns True if all elements are Decimal.
- **a**: List or tuple of values or a value
- **b**: True for list/tuple of values and False for a value
        '''
        if b is not True:
            if a.__class__.__name__=='Decimal':return False
        if ((ta:=a.__class__.__name__)=='list' or ta=='tuple') and b is True:
            for i in a:
                if i.__class__.__name__!='Decimal':return False
            return True
        else:print("{} is not 'list'/'tuple'".format(ta))


def eqval(a,b)->bool:
    '''
#### Returns True if values are equal.
 - **a, b**: values
    '''
    try:
        if a==b:return True;
        else:raise Exception(str(a)+" != "+str(b));
    except Exception as e:retrn('c',e);


def tbool(a:list|tuple,b=None)->bool:
    '''
#### Returns True if all values are boolean.
- **a**: List or tuple of values or a value
- **b**: True for list or tuple of values and False for a single value
    '''
    try:
        if (ta:=a.__class__.__name__)=='bool':return True;
        if (ta=='list' or ta=='tuple') and b is True:
            for i in a:
                if (ti:=i.__class__.__name__)!='bool':raise Exception("'{}' is not 'bool'".format(ti));
            return True
        else:raise Exception(ta+" is not bool");
    except Exception as e:retrn('c',e);

# return True if matx
def tmatx(a:tuple|list,b=None)->bool:
    '''
#### Returns True if all values are matx objects.
- **a**: List or tuple of values or a value
- **b**: True for list or tuple of values and False for a single value
    '''
    try:
        if (ta:=a.__class__.__name__)=='matx':return True;
        if (ta=='list' or ta=='tuple') and b is True:
            for i in a:
                if (ti:=i.__class__.__name__)!='matx':raise Exception("'{}' is not 'matx'".format(ti));
            return True
        else:raise Exception(ta+" is not matx");
    except Exception as e:retrn('c',e);


# return True if tuple
def ttup(a:tuple|tuple[tuple,...])->bool:
    '''
#### Returns True if tuple or tuple of tuples.
- **a**: Value or tuple of values
    '''
    try:
        if (ta:=a.__class__.__name__)=='tuple':
            if (ta0:=a[0].__class__.__name__)==ta:
                for i in range(1,len(a)):
                    if (ti:=a[i].__class__.__name__)!=ta0:raise Exception("'{}' is not 'tuple'".format(ti));
                return True
            else:return True;
        else:raise Exception(ta+" is not tuple");
    except Exception as e:retrn('c',e);

# return list if list
def tlist(a:list|list[list])->bool:
    '''
#### Returns True if list or list of lists.
- **a**: Value or list of values
    '''
    try:
        if (ta:=a.__class__.__name__)=='list':
            if (ta0:=a[0].__class__.__name__)==ta:
                for i in range(1,len(a)):
                    if (ti:=a[i].__class__.__name__)!=ta0:raise Exception("'{}' is not 'list'".format(ti));
                return True
            else:return True;
        else:raise Exception(ta+" is not list");
    except Exception as e:retrn('c',e);


# return True if lengths of lists are equal
def eqllen(a:list[list]|tuple[list,...]|tuple[tuple,...]|list[tuple])->bool:
    '''
#### Returns True if list or tuple has lists or tuples of equal lengths.
- **a**: List/tuple of lists or tuples
    '''
    try:
        if (ta:=a.__class__.__name__)=='tuple' or ta=='list':
            l0=len(a[0]);c=0;
            if (l:=len(a))==1:return True;
            while (c:=c+1)!=l:
                if (li:=len(a[c]))!=l0:raise Exception(li+" != "+l0);
                return True
        else:raise Exception("Invalid argument: a => list/tuple");
    except Exception as e:retrn('c',e);


# return true if data
def tdata(d:list|tuple,b=None)->bool:
    '''
#### Returns True if data object or list/tuple of data objects.
- **d**: Object or list/tuple of objects
- **b**: True for list/tuple of objects and False for a single object
    '''
    try:
        if (td:=d.__class__.__name__)=='data':return True;
        if (td=='list' or td=='tuple') and b is True:
            for i in d:
                if (ti:=i.__class__.__name__)!='data':raise Exception("'{}' is not 'data'".format(ti));
            return True
        else:raise Exception("'{}' is not 'data'".format(td));
    except Exception as e:retrn('c',e);

def tstr(li:str|tuple|list,b=None)->bool:
    '''
#### Returns True if type is 'str'
- **li**: Value or list/tuple of values
- **b**: True for list/tuple of values and False for a single value
    '''
    try:
        if (tli:=li.__class__.__name__)=='str':return True
        if (tli=='list' or tli=='tuple') and b is True:
            for i in li:
                if i.__class__.__name__!='str':raise Exception("'{}' is not 'str'".format(i.__class__.__name__))
    except Exception as e:retrn('c',e);

class tfunc:

    @staticmethod
    def axn(a)->bool:
        '''
#### Returns True if axn object.
- **a**: Object
        '''
        try:
            if (ta:=a.__class__.__name__)=='axn':return True;
            else:raise Exception(ta+" is not axn");
        except Exception as e:retrn('c',e);

    @staticmethod
    def poly(a)->bool:
        '''
#### Returns True if poly object.
- **a**: Object
        '''
        try:
            if (ta:=a.__class__.__name__)=='poly':return True;
            else:raise Exception(ta+" is not poly");
        except Exception as e:retrn('c',e);

    @staticmethod
    def apolyn(a)->bool:
        '''
#### Returns True if apolyn object.
- **a**: Object
        '''
        try:
            if (ta:=a.__class__.__name__)=='apolyn':return True;
            else:raise Exception(ta+" is not apolyn");
        except Exception as e:retrn('c',e);


class tdict:

    @staticmethod
    def dic(a:dict)->bool:
        '''
#### Returns True if dictionary.
- **a**: Object
        '''
        try:
            if (ta:=a.__class__.__name__)=='dict':return True;
            else:raise Exception(ta+" is not dict");
        except Exception as e:retrn('c',e);

    @classmethod
    def matchkeys(cls,a:dict,b:dict)->bool:
        '''
#### Returns True if all keys match for two dictionaries.
- **a**: Dictionary
- **b**: Dictionary
        '''
        try:
            if cls.dic(a) is None or cls.dic(b) is None:raise Exception;
            a=a.keys();b=list(b.keys());
            if (la:=len(a))!=(lb:=len(b)):raise Exception(la+" != "+lb);
            for i in a:b.remove(i);
            if len(b)==0:return True;
            else:raise Exception;
        except Exception:retrn('c',"Keys are not same");
