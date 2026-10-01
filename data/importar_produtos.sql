BEGIN TRANSACTION;

DELETE FROM produtos;

INSERT INTO produtos
(codigo, codigo_busca, zona, localizacao, tipo, material, cores, quantidade, observacao)
VALUES
('HA-21575','HA21575','C1','centro frente da loja','produto','','',1,''),
('BC-21592','BC21592','C1','centro frente da loja','mochila','','',1,'mochila'),
('HO-21714','HO21714','C1','centro frente da loja','mochila','','',1,'mochila'),
('HO-21716','HO21716','C1','centro frente da loja','mochila','','',1,'mochila'),
('NE-21521','NE21521','C1','centro frente da loja','produto','','',1,''),

('HO-21370','HO21370','C2','Casulo 2','produto','','',1,''),
('HO-21217','HO21217','C2','Casulo 2','produto','','',1,''),
('NE-21532','NE21532','C2','Casulo 2','produto','','',1,''),
('HO-21367','HO21367','C2','Casulo 2','produto','','',1,''),
('HO-19937','HO19937','C2','Casulo 2','produto','','',1,''),
('NE-21240','NE21240','C2','Casulo 2','produto','','',1,''),
('HO-21216','HO21216','C2','Casulo 2','produto','','',1,''),

('HO-21914','HO21914','C3','Casulo 3','produto','','',1,''),
('HA-21351','HA21351','C3','Casulo 3','produto','','',1,''),
('HO-21543','HO21543','C3','Casulo 3','produto','','',1,''),
('HO-21740','HO21740','C3','Casulo 3','produto','','',1,''),
('NE-20974','NE20974','C3','Casulo 3','produto','','',1,''),

('HA-21584','HA21584','C4','Casulo 4','produto','','',1,''),
('HO-21326','HO21326','C4','Casulo 4','produto','','',1,''),
('HO-21327','HO21327','C4','Casulo 4','produto','','',1,''),
('HO-20760','HO20760','C4','Casulo 4','produto','','',1,''),
('HO-20726','HO20726','C4','Casulo 4','produto','','',1,''),
('MG-21686','MG21686','C4','Casulo 4','produto','','',1,''),
('MG-21687','MG21687','C4','Casulo 4','produto','','',1,''),

('HO-20987','HO20987','C5','Casulo 5','produto','','',1,''),
('HO-21223','HO21223','C5','Casulo 5','produto','','',1,''),
('HO-21550','HO21550','C5','Casulo 5','produto','','',1,''),
('HO-21218','HO21218','C5','Casulo 5','produto','','',1,''),
('HO-21894','HO21894','C5','Casulo 5','produto','','',1,''),
('YY-21874','YY21874','C5','Casulo 5','produto','','',1,''),

('HO-21556','HO21556','C6','Casulo 6','produto','','',1,''),
('HA-21148','HA21148','C6','Casulo 6','produto','','',1,''),
('HO-21560','HO21560','C6','Casulo 6','produto','','',1,''),
('HA-21176','HA21176','C6','Casulo 6','produto','','',1,''),
('HO-21205','HO21205','C6','Casulo 6','produto','','',1,'Algumas peças do HO-21205 estão no mesmo casulo pois está cheio'),
('HO-20979','HO20979','C6','Casulo 6','produto','','',1,''),
('HO-21202','HO21202','C6','Casulo 6','produto','','',1,''),
('HO-21904','HO21904','C6','Casulo 6','produto','','',1,''),

('HO-21208','HO21208','C7','Casulo 7','produto','','',1,''),
('HA-21174','HA21174','C7','Casulo 7','produto','','',1,''),
('HO-20339','HO20339','C7','Casulo 7','produto','','',1,''),

('HO-21452','HO21452','C8','Casulo 8','produto','','',1,''),
('HA-21580','HA21580','C8','Casulo 8','produto','','',1,''),
('HO-21737','HO21737','C8','Casulo 8','produto','','',1,''),
('NE-21835','NE21835','C8','Casulo 8','produto','','',1,''),
('NE-21525','NE21525','C8','Casulo 8','produto','','',1,''),

('HO-21549','HO21549','C9','Casulo 9','produto','','',1,''),
('BC-21594','BC21594','C9','Casulo 9','mochila','','',1,'mochila'),

('HO-21331','HO21331','C10','Casulo 10','produto','','',1,''),
('HO-21002','HO21002','C10','Casulo 10','produto','','',1,''),
('MG-21685','MG21685','C10','Casulo 10','produto','','',1,''),
('HA-21359','HA21359','C10','Casulo 10','produto','','',1,''),

('HO-20762','HO20762','C11','Casulo 11','mochila','','',1,'mochila'),
('HO-21566','HO21566','C11','Casulo 11','produto','','',1,''),

('HA-21589','HA21589','C12','Casulo 12','produto','','',1,''),
('HO-21369','HO21369','C12','Casulo 12','produto','','',1,''),

('HO-21245','HO21245','C13','Casulo 13','produto','','',1,''),
('HO-21893','HO21893','C13','Casulo 13','produto','','',1,''),
('HA-21164','HA21164','C13','Casulo 13','produto','','',1,''),
('HO-21541','HO21541','C13','Casulo 13','produto','','',1,''),
('HA-21167','HA21167','C13','Casulo 13','produto','','',1,''),
('HO-21366','HO21366','C13','Casulo 13','produto','','',1,''),

('HO-21006','HO21006','C14','Casulo 14','produto','','',1,''),
('HO-20981','HO20981','C14','Casulo 14','produto','','',1,''),
('HA-21348','HA21348','C14','Casulo 14','produto','','',1,''),
('HA-21363','HA21363','C14','Casulo 14','produto','','',1,''),

('YY-21871','YY21871','C15','Casulo 15','produto','','',1,''),
('HA-21358','HA21358','C15','Casulo 15','produto','','',1,''),
('HO-21329','HO21329','C15','Casulo 15','produto','','',1,''),
('NE-21531','NE21531','C15','Casulo 15','produto','','',1,''),

('HA-21155','HA21155','C16','Casulo 16','produto','','',1,''),
('HO-21900','HO21900','C16','Casulo 16','produto','','',1,''),
('HO-20982','HO20982','C16','Casulo 16','produto','','',1,''),
('HO-21561','HO21561','C16','Casulo 16','produto','','',1,''),
('HO-20984','HO20984','C16','Casulo 16','produto','','',1,''),

('HA-21579','HA21579','C17','Casulo 17','produto','','',1,''),
('HO-21368','HO21368','C17','Casulo 17','produto','','',1,''),
('HO-21733','HO21733','C17','Casulo 17','produto','','',1,''),
('BC-21591','BC21591','C17','Casulo 17','mochila','','',1,'mochila'),
('HO-21003','HO21003','C17','Casulo 17','produto','','',1,''),

('HA-21848','HA21848','ESC','Pé da escada piso loja','produto','','',1,''),
('HO-21364','HO21364','ESC','Pé da escada piso loja','produto','','',1,''),
('HA-21574','HA21574','ESC','Pé da escada piso loja','produto','','',1,''),

('HO-21744','HO21744','CX','Frente do caixa e sequência','produto','','',1,''),
('HO-22354','HO22354','CX','Frente do caixa e sequência','produto','','',1,''),
('HO-21544','HO21544','CX','Frente do caixa e sequência','produto','','',1,''),
('HO-21883','HO21883','CX','Frente do caixa e sequência','produto','','',1,''),
('HO-22073','HO22073','CX','Frente do caixa e sequência','produto','','',1,''),

('BC-21593','BC21593','URS','Em frente do balcão dos chaveirinhos de ursinhos','mochila','','',1,'mochila'),
('NE-21836','NE21836','URS','Em frente do balcão dos chaveirinhos de ursinhos','produto','','',1,''),

('HO-21755','HO21755','CART','Em frente às carteiras','produto','','',1,''),
('HO-21890','HO21890','CART','Em frente às carteiras','produto','','',1,''),
('HO-21451','HO21451','CART','Em frente às carteiras','produto','','',1,''),
('HO-21372','HO21372','CART','Em frente às carteiras','produto','','',1,''),
('HO-21734','HO21734','CART','Em frente às carteiras','mochila','','',1,'mochila'),
('HO-21896','HO21896','CART','Em frente às carteiras','produto','','',1,''),
('HA-21577','HA21577','CART','Em frente às carteiras','produto','','',1,''),
('HO-21735','HO21735','CART','Em frente às carteiras','mochila','','',1,'mochila'),
('HO-21749','HO21749','CART','Em frente às carteiras','produto','','',1,''),
('HO-20987','HO20987','CART','Em frente às carteiras','produto','','',1,'Também localizado no Casulo 5'),

('HO-21548','HO21548','FC7','Em frente ao Casulo 7','produto','','',1,''),
('HO-21542','HO21542','FC7','Em frente ao Casulo 7','produto','','',1,''),
('HO-21545','HO21545','FC7','Em frente ao Casulo 7','produto','','',1,''),
('HO-21251','HO21251','FC7','Em frente ao Casulo 7','mochila','','',1,'mochila'),
('HO-21221','HO21221','FC7','Em frente ao Casulo 7','produto','','',1,''),
('HO-21546','HO21546','FC7','Em frente ao Casulo 7','produto','','',1,''),
('HO-21912','HO21912','FC7','Em frente ao Casulo 7','produto','','',1,'');

COMMIT;
