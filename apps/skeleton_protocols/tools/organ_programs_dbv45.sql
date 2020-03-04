SELECT 	OGP.Name AS ris_name,
		Exam.Name AS exam_name,
		BodyPart.Name AS body_part,
		AcquisitionSystem.Name AS acquisition_system,
		Technique.Value AS technique,
		OGP_kV.Value AS kv,
		RADOGP_mAs.Value AS mas,
		FilterType.Name AS filter_cu,
		Focus.Name AS focus,
		DiamondViewID.Name AS diamond_view,
		EdgeFilterKernel.Value AS edge_filter_kernel_size,
		SpatialFrequencyParameter.Edgefiltergain AS edge_filter_gain,
		HarmonisKernel.Value AS harmonization_kernel_size,
		SpatialFrequencyParameter.Harmonisgain AS harmonization_gain,
		SpatialFrequencyParameter.Noisereduction AS noise_reduction,
		RAD_OGP.Imageautoamplification AS image_auto_amplification,
		ImageAmplification.Value AS image_amplification_gain,
		Dose_RAD.Sensitivity AS sensitivity,
		GradationParameter.Name AS lut,
		FPSet.Name AS fp_set
FROM OGP

INNER JOIN Exam_OGP ON OGP.Id = Exam_OGP.Id_ogp
INNER JOIN Exam ON Exam.Id = Exam_OGP.Id_exam
INNER JOIN BodyPart ON BodyPart.Id = OGP.Id_bodypart
INNER JOIN AcquisitionSystem ON AcquisitionSystem.Id = OGP.Id_acqsystem
INNER JOIN OGP_kV  ON OGP_kV.ID = OGP.ID_kV
INNER JOIN RAD_OGP ON RAD_OGP.ID = OGP.ID
LEFT OUTER JOIN RADOGP_mAs ON RAD_OGP.Id_mas = RADOGP_mAs.Id
INNER JOIN Technique ON RAD_OGP.Id_technique = Technique.Id
INNER JOIN FilterType ON OGP.Id_filtertype = FilterType.Id
INNER JOIN Focus ON OGP.Id_focus = Focus.Id
INNER JOIN SpatialFrequencyParameter ON OGP.Id_imaspatialfreqparam = SpatialFrequencyParameter.Id
INNER JOIN DiamondViewID ON SpatialFrequencyParameter.Id_diamondviewid = DiamondViewID.Id
INNER JOIN EdgeFilterKernel ON SpatialFrequencyParameter.Id_edgefilterkernel = EdgeFilterKernel.Id
INNER JOIN HarmonisKernel ON SpatialFrequencyParameter.Id_harmoniskernel = HarmonisKernel.Id
LEFT OUTER JOIN ImageAmplification ON RAD_OGP.Id_imageamplification = ImageAmplification.Id
INNER JOIN Dose_RAD ON RAD_OGP.Id_dose = Dose_RAD.Id
INNER JOIN GradationParameter ON RAD_OGP.Id_imagegradation = GradationParameter.Ids
LEFT OUTER JOIN FPSet ON FPset.ID = OGP.ID_FPSet


WHERE
OGP.status=2
AND OGP.Type='SIEMENSDEFAULT'
AND NOT OGP.Id_bodypart=57
AND ris_name NOT LIKE '-%'
AND ris_name NOT LIKE '. _%'
AND ris_name NOT LIKE '%\_%' ESCAPE '\'