-- Reset filename with article information
UPDATE cfiledata
LEFT JOIN carticle ON carticle.id=cfiledata.entity_id
SET cfiledata.oldfilename=CONCAT(cfiledata.documenttype, '_', carticle.article, '_', carticle.id, '_', cfiledata.id, RIGHT(oldfilename,4))
WHERE cfiledata.entity_type='carticle' and entity_id in (SELECT id from carticle WHERE carticle.family_id=280);

-- Reset filename with family information
UPDATE cfiledata
LEFT JOIN cfamily ON cfamily.id=cfiledata.entity_id
SET cfiledata.oldfilename=CONCAT(cfiledata.documenttype, '_', cfamily.family, '_', cfamily.id, '_', cfiledata.id, RIGHT(oldfilename,4))
WHERE cfiledata.entity_type='cfamily' and entity_id=280;

-- Reset filename with article info for full catalog
UPDATE cfiledata
LEFT JOIN carticle ON cfiledata.entity_id=carticle.id
SET cfiledata.oldfilename=CONCAT(cfiledata.documenttype, '_', carticle.article, '_', carticle.id, '_', cfiledata.id, RIGHT(oldfilename,4))
WHERE cfiledata.entity_type='carticle' and cfiledata.entity_id in 
(SELECT 
 	carticle.id FROM carticle 
 LEFT JOIN cfamily ON carticle.family_id=cfamily.id 
 LEFT JOIN cproductgroup ON cproductgroup.id=cfamily.product_group_id
 LEFT JOIN ccatalog ON ccatalog.id=cproductgroup.catalog_id
 WHERE ccatalog.id=2
);


-- Reset filename with family info for full catalog
UPDATE cfiledata
LEFT JOIN cfamily ON cfiledata.entity_id=cfamily.id
SET cfiledata.oldfilename=CONCAT(cfiledata.documenttype, '_', cfamily.family, '_', cfamily.id, '_', cfiledata.id, RIGHT(oldfilename,4))
WHERE cfiledata.entity_type='cfamily' and cfiledata.entity_id in 
(SELECT 
 	cfamily.id FROM cfamily 
 LEFT JOIN cproductgroup ON cproductgroup.id=cfamily.product_group_id
 LEFT JOIN ccatalog ON ccatalog.id=cproductgroup.catalog_id
 WHERE ccatalog.id=2
);
